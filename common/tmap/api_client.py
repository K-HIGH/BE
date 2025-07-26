"""
T-map API 클라이언트 모듈

T-map API의 대중교통 길찾기 기능을 제공하는 클라이언트입니다.
- 대중교통 길찾기 (지하철, 버스)
- 보행자 + 대중교통 통합 경로
- 실시간 교통 정보 반영

사용 방법:
    client = TmapClient(api_key="your_tmap_api_key")
    result = await client.get_transit_directions(origin, destination)

의존성:
    - httpx: HTTP 클라이언트
    - pydantic: 데이터 모델
"""

import os
import math
import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

import httpx
from pydantic import BaseModel, Field


# 로깅 설정
logger = logging.getLogger(__name__)


# DTO 모델들
class TmapCoordinate(BaseModel):
    """T-map 좌표 정보 모델"""
    lon: float = Field(..., description="경도 (longitude)")
    lat: float = Field(..., description="위도 (latitude)")


class TransitRouteRequest(BaseModel):
    """대중교통 길찾기 요청 모델"""
    start_x: float = Field(..., description="출발지 경도")
    start_y: float = Field(..., description="출발지 위도")
    end_x: float = Field(..., description="도착지 경도")
    end_y: float = Field(..., description="도착지 위도")
    format: str = Field("json", description="응답 형식")
    count: int = Field(10, description="경로 개수 (최대 10개)")
    lang: int = Field(0, description="언어 설정 (0: 한국어, 1: 영어)")
    route_info: int = Field(0, description="경로 정보 (0: 기본, 1: 상세)")


class TransitStep(BaseModel):
    """대중교통 구간 정보"""
    step_type: str = Field(..., description="구간 타입 (WALK, SUBWAY, BUS)")
    distance: int = Field(..., description="거리 (m)")
    duration: int = Field(..., description="소요시간 (분)")
    line_name: Optional[str] = Field(None, description="노선명")
    start_name: Optional[str] = Field(None, description="출발 정류장/역명")
    end_name: Optional[str] = Field(None, description="도착 정류장/역명")
    instruction: Optional[str] = Field(None, description="안내 메시지")


class TransitRoute(BaseModel):
    """대중교통 경로 정보"""
    total_time: int = Field(..., description="총 소요시간 (분)")
    total_distance: int = Field(..., description="총 거리 (m)")
    total_walk_time: int = Field(..., description="총 도보시간 (분)")
    bus_transit_count: int = Field(..., description="버스 환승 횟수")
    subway_transit_count: int = Field(..., description="지하철 환승 횟수")
    total_fare: int = Field(..., description="총 요금 (원)")
    steps: List[TransitStep] = Field(..., description="경로 구간 목록")


class TransitDirectionsResponse(BaseModel):
    """대중교통 길찾기 응답 모델"""
    result_code: int = Field(..., description="결과 코드")
    result_msg: str = Field(..., description="결과 메시지")
    routes: List[TransitRoute] = Field(..., description="경로 목록")


class TmapError(Exception):
    """T-map API 에러 클래스"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, error_code: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class TmapClient:
    """
    T-map API 클라이언트
    
    T-map API를 통한 대중교통 길찾기 기능을 제공합니다.
    모든 API 호출은 비동기로 처리됩니다.
    
    Attributes:
        api_key: T-map API 키
        base_url: API 기본 URL
        timeout: 요청 타임아웃 (초)
        
    Example:
        >>> client = TmapClient(api_key="your_tmap_api_key")
        >>> origin = TmapCoordinate(lon=127.108678, lat=37.402001)
        >>> dest = TmapCoordinate(lon=127.108764, lat=37.402127)
        >>> result = await client.get_transit_directions(origin, dest)
    """
    
    def __init__(
        self, 
        api_key: str,
        base_url: str = "https://apis.openapi.sk.com",
        timeout: int = 30
    ):
        """
        클라이언트 초기화
        
        Args:
            api_key: T-map API 키
            base_url: API 기본 URL
            timeout: 요청 타임아웃 (초)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self._client = None
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers={
                "appKey": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
                # "User-Agent": "TmapClient/1.0"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self._client:
            await self._client.aclose()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        API 요청 실행
        
        Args:
            method: HTTP 메서드
            endpoint: API 엔드포인트
            params: 쿼리 파라미터
            json_data: JSON 데이터
            
        Returns:
            API 응답 데이터
            
        Raises:
            TmapError: API 요청 실패 시
        """
        if not self._client:
            raise TmapError("클라이언트가 초기화되지 않았습니다. async with 문을 사용해주세요.")
        
        url = f"{self.base_url}{endpoint}"
        
        # 디버깅을 위한 로깅
        logger.info(f"T-map API 요청: {method} {url}")
        logger.info(f"파라미터: {params}")
        if json_data:
            logger.info(f"JSON 데이터: {json_data}")
        logger.info(f"헤더: {self._client.headers}")
        
        try:
            response = await self._client.request(
                method=method,
                url=url,
                params=params,
                json=json_data
            )
            
            # 응답 로깅
            logger.info(f"응답 상태코드: {response.status_code}")
            logger.info(f"응답 헤더: {dict(response.headers)}")
            if response.content:
                logger.info(f"응답 내용 (처음 500자): {response.text[:500]}")
            
            # 응답 상태 코드 확인
            if response.status_code != 200:
                try:
                    error_data = response.json() if response.content else {}
                    # T-map API 에러 응답 구조에 맞춰 파싱
                    if "error" in error_data:
                        error_info = error_data["error"]
                        error_message = error_info.get("message", f"HTTP {response.status_code} 오류")
                        error_code = error_info.get("code", "UNKNOWN_ERROR")
                    else:
                        # 다른 형식의 에러 응답
                        error_message = error_data.get("message", error_data.get("msg", f"HTTP {response.status_code} 오류"))
                        error_code = error_data.get("code", error_data.get("errorCode", "UNKNOWN_ERROR"))
                except:
                    error_message = f"HTTP {response.status_code} 오류: {response.text[:200] if response.text else 'No content'}"
                    error_code = "HTTP_ERROR"
                
                raise TmapError(
                    message=error_message,
                    status_code=response.status_code,
                    error_code=error_code
                )
            
            return response.json()
            
        except httpx.TimeoutException:
            raise TmapError("요청 타임아웃이 발생했습니다.")
        except httpx.RequestError as e:
            raise TmapError(f"네트워크 오류: {str(e)}")
        except Exception as e:
            if isinstance(e, TmapError):
                raise
            raise TmapError(f"예상치 못한 오류: {str(e)}")
    
    async def get_transit_directions(
        self,
        origin: TmapCoordinate,
        destination: TmapCoordinate,
        count: int = 3,
        lang: int = 0,
        route_info: int = 1
    ) -> TransitDirectionsResponse:
        """
        대중교통 길찾기 요청
        
        Args:
            origin: 출발지 좌표
            destination: 도착지 좌표
            count: 경로 개수 (최대 10개)
            lang: 언어 설정 (0: 한국어, 1: 영어)
            route_info: 경로 정보 (0: 기본, 1: 상세)
            
        Returns:
            대중교통 길찾기 결과
            
        Raises:
            TmapError: API 요청 실패 시
            
        Example:
            >>> origin = TmapCoordinate(lon=127.108678, lat=37.402001)
            >>> dest = TmapCoordinate(lon=127.108764, lat=37.402127)
            >>> result = await client.get_transit_directions(origin, dest)
        """
        # JSON 데이터 구성 (T-map 대중교통 API는 POST 메소드 사용)
        json_data = {
            "startX": str(origin.lon),
            "startY": str(origin.lat),
            "endX": str(destination.lon),
            "endY": str(destination.lat),
            "format": "json",
            "count": count,
            "lang": lang,
            # "routeInfo": route_info
        }
        
        # API 요청 (T-map 대중교통 길찾기 API - POST 메소드)
        data = await self._make_request("POST", "/transit/routes", json_data=json_data)
        
        # 응답 데이터 파싱
        routes = []
        if "metaData" in data and "plan" in data["metaData"]:
            plan_data = data["metaData"]["plan"]
            itineraries = plan_data.get("itineraries", [])
            
            for itinerary in itineraries:
                # 경로 기본 정보
                total_time = itinerary.get("totalTime", 0)
                total_distance = itinerary.get("totalDistance", 0)
                total_walk_time = itinerary.get("totalWalkTime", 0)
                bus_transit_count = itinerary.get("busTransitCount", 0)
                subway_transit_count = itinerary.get("subwayTransitCount", 0)
                total_fare = itinerary.get("fare", {}).get("regular", {}).get("totalFare", 0)
                
                # 경로 구간 정보
                steps = []
                legs = itinerary.get("legs", [])
                
                for leg in legs:
                    mode = leg.get("mode", "WALK")
                    distance = leg.get("distance", 0)
                    duration = leg.get("sectionTime", 0)
                    
                    # 구간 타입별 처리
                    if mode == "WALK":  # 도보
                        step = TransitStep(
                            step_type="WALK",
                            distance=distance,
                            duration=duration,
                            instruction="도보 이동"
                        )
                    elif mode == "BUS":  # 버스
                        route = leg.get("route", "")
                        start_name = leg.get("start", {}).get("name", "")
                        end_name = leg.get("end", {}).get("name", "")
                        
                        step = TransitStep(
                            step_type="BUS",
                            distance=distance,
                            duration=duration,
                            line_name=route,
                            start_name=start_name,
                            end_name=end_name,
                            instruction=f"{route}번 버스 탑승"
                        )
                    elif mode == "SUBWAY":  # 지하철
                        route = leg.get("route", "")
                        start_name = leg.get("start", {}).get("name", "")
                        end_name = leg.get("end", {}).get("name", "")
                        
                        step = TransitStep(
                            step_type="SUBWAY",
                            distance=distance,
                            duration=duration,
                            line_name=route,
                            start_name=start_name,
                            end_name=end_name,
                            instruction=f"{route} 탑승"
                        )
                    else:
                        # 기타 교통수단
                        step = TransitStep(
                            step_type=mode,
                            distance=distance,
                            duration=duration,
                            instruction=f"{mode} 이용"
                        )
                    
                    steps.append(step)
                
                # 경로 객체 생성
                route = TransitRoute(
                    total_time=total_time,
                    total_distance=total_distance,
                    total_walk_time=total_walk_time,
                    bus_transit_count=bus_transit_count,
                    subway_transit_count=subway_transit_count,
                    total_fare=total_fare,
                    steps=steps
                )
                routes.append(route)
        
        return TransitDirectionsResponse(
            result_code=0,
            result_msg="SUCCESS",
            routes=routes
        )
    
    async def get_pedestrian_route(
        self,
        origin: TmapCoordinate,
        destination: TmapCoordinate,
        speed: int = 4
    ) -> Dict[str, Any]:
        """
        보행자 경로 탐색
        
        Args:
            origin: 출발지 좌표
            destination: 도착지 좌표
            speed: 보행 속도 (km/h, 기본값: 4)
            
        Returns:
            보행자 경로 정보
            
        Raises:
            TmapError: API 요청 실패 시
        """
        # 파라미터 구성
        params = {
            "startX": origin.lon,
            "startY": origin.lat,
            "endX": destination.lon,
            "endY": destination.lat,
            "reqCoordType": "WGS84GEO",
            "resCoordType": "WGS84GEO",
            "angle": 0,
            "searchOption": 0,
            "speed": speed
        }
        
        # T-map 보행자 길찾기 API 요청
        json_data = {
            "startX": str(origin.lon),
            "startY": str(origin.lat),
            "endX": str(destination.lon),
            "endY": str(destination.lat),
            "reqCoordType": "WGS84GEO",
            "resCoordType": "WGS84GEO",
            "angle": 0,
            "searchOption": 0,
            "speed": speed
        }
        
        data = await self._make_request("POST", "/tmap/routes/pedestrian", json_data=json_data)
        
        return data
    
    def calculate_distance(self, coord1: TmapCoordinate, coord2: TmapCoordinate) -> float:
        """
        두 좌표 간의 직선 거리 계산 (하버사인 공식)
        
        Args:
            coord1: 첫 번째 좌표
            coord2: 두 번째 좌표
            
        Returns:
            거리 (km)
        """
        # 지구 반지름 (km)
        R = 6371.0
        
        # 라디안으로 변환
        lat1_rad = math.radians(coord1.lat)
        lon1_rad = math.radians(coord1.lon)
        lat2_rad = math.radians(coord2.lat)
        lon2_rad = math.radians(coord2.lon)
        
        # 차이값 계산
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # 하버사인 공식 적용
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c


# 편의 함수들
async def get_transit_directions(
    api_key: str,
    origin: TmapCoordinate,
    destination: TmapCoordinate,
    count: int = 3
) -> TransitDirectionsResponse:
    """
    간편 대중교통 길찾기 함수
    
    Args:
        api_key: T-map API 키
        origin: 출발지
        destination: 도착지
        count: 경로 개수
        
    Returns:
        대중교통 길찾기 결과
    """
    async with TmapClient(api_key=api_key) as client:
        return await client.get_transit_directions(origin, destination, count)


# 사용 예시
if __name__ == "__main__":
    
    from dotenv import load_dotenv
    load_dotenv(".env")
    
    print("T-map API Key:", os.getenv("TMAP_API_KEY"))
    
    async def example():
        """사용 예시"""
        api_key = os.getenv("TMAP_API_KEY")
        
        if not api_key:
            print("T-map API 키가 설정되지 않았습니다.")
            return
        
        # 좌표 설정 (강남역 -> 역삼역)
        origin = TmapCoordinate(lon=127.027926, lat=37.497175)  # 강남역
        destination = TmapCoordinate(lon=127.035399, lat=37.500489)  # 역삼역
        
        # 클라이언트 사용
        async with TmapClient(api_key=api_key) as client:
            try:
                # 대중교통 길찾기
                transit_result = await client.get_transit_directions(origin, destination)
                print(f"대중교통 경로 개수: {len(transit_result.routes)}")
                
                if transit_result.routes:
                    route = transit_result.routes[0]
                    print(f"총 소요시간: {route.total_time}분")
                    print(f"총 거리: {route.total_distance}m")
                    print(f"총 요금: {route.total_fare}원")
                    print(f"환승 횟수: 버스 {route.bus_transit_count}회, 지하철 {route.subway_transit_count}회")
                    
                    print("\n=== 경로 상세 ===")
                    for i, step in enumerate(route.steps, 1):
                        print(f"{i}. {step.step_type}: {step.instruction}")
                        if step.line_name:
                            print(f"   노선: {step.line_name}")
                        if step.start_name and step.end_name:
                            print(f"   {step.start_name} → {step.end_name}")
                        print(f"   거리: {step.distance}m, 소요시간: {step.duration}분")
                        print()
                
                # 직선 거리 계산
                distance = client.calculate_distance(origin, destination)
                print(f"직선 거리: {distance:.2f}km")

                for route in transit_result.routes:
                    print(route)
                
            except TmapError as e:
                print(f"T-map API 오류: {e.message}")
                if e.status_code:
                    print(f"상태 코드: {e.status_code}")
                if e.error_code:
                    print(f"에러 코드: {e.error_code}")
                raise e
            except Exception as e:
                print(f"예상치 못한 오류: {str(e)}")
    
    # 예시 실행
    asyncio.run(example()) 