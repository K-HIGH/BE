"""
카카오 지도 API 클라이언트 모듈

카카오 지도 API의 길찾기 기능을 제공하는 클라이언트입니다.
- 자동차 길찾기
- 보행자 길찾기
- 좌표 변환 등의 기능을 포함합니다.

사용 방법:
    client = KakaoMapClient(api_key="your_api_key")
    result = await client.get_car_directions(origin, destination)

의존성:
    - httpx: HTTP 클라이언트
    - pydantic: 데이터 모델
"""
import os
import math
import asyncio
import logging
from typing import Optional, List, Dict, Any
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel, Field


# 로깅 설정
logger = logging.getLogger(__name__)


# DTO 모델들
class Coordinate(BaseModel):
    """좌표 정보 모델"""
    x: float = Field(..., description="경도 (longitude)")
    y: float = Field(..., description="위도 (latitude)")


class RouteRequest(BaseModel):
    """길찾기 요청 모델"""
    origin: Coordinate = Field(..., description="출발지 좌표")
    destination: Coordinate = Field(..., description="도착지 좌표")
    waypoints: Optional[List[Coordinate]] = Field(None, description="경유지 좌표 목록")
    priority: Optional[str] = Field("RECOMMEND", description="길찾기 옵션 (RECOMMEND, TIME, DISTANCE)")
    car_fuel: Optional[str] = Field("GASOLINE", description="연료 타입 (GASOLINE, DIESEL, LPG)")
    car_hipass: Optional[bool] = Field(False, description="하이패스 사용 여부")
    alternatives: Optional[bool] = Field(False, description="대안 경로 제공 여부")


class WalkingRouteRequest(BaseModel):
    """보행자 길찾기 요청 모델"""
    origin: Coordinate = Field(..., description="출발지 좌표")
    destination: Coordinate = Field(..., description="도착지 좌표")


class Road(BaseModel):
    """도로 정보 모델"""
    name: str = Field(..., description="도로명")
    distance: int = Field(..., description="도로 거리 (m)")
    duration: int = Field(..., description="소요시간 (초)")
    traffic_speed: float = Field(..., description="교통 속도")
    traffic_state: int = Field(..., description="교통 상황 (0: 원활, 1: 서행, 2: 정체)")


class Route(BaseModel):
    """경로 정보 모델"""
    result_code: int = Field(..., description="결과 코드")
    result_msg: str = Field(..., description="결과 메시지")
    summary: Dict[str, Any] = Field(..., description="경로 요약 정보")
    sections: List[Dict[str, Any]] = Field(..., description="구간별 상세 정보")


class DirectionsResponse(BaseModel):
    """길찾기 응답 모델"""
    trans_id: str = Field(..., description="요청 ID")
    routes: List[Route] = Field(..., description="경로 목록")


class KakaoMapError(Exception):
    """카카오 지도 API 에러 클래스"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, error_code: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class KakaoMapClient:
    """
    카카오 지도 API 클라이언트
    
    카카오 지도 API를 통한 길찾기, 좌표 변환 등의 기능을 제공합니다.
    모든 API 호출은 비동기로 처리됩니다.
    
    Attributes:
        api_key: 카카오 REST API 키
        base_url: API 기본 URL
        timeout: 요청 타임아웃 (초)
        
    Example:
        >>> client = KakaoMapClient(api_key="your_api_key")
        >>> origin = Coordinate(x=127.108678, y=37.402001)
        >>> dest = Coordinate(x=127.108764, y=37.402127)
        >>> result = await client.get_car_directions(origin, dest)
    """
    
    def __init__(
        self, 
        api_key: str,
        base_url: str = "https://apis-navi.kakaomobility.com",
        timeout: int = 30
    ):
        """
        클라이언트 초기화
        
        Args:
            api_key: 카카오 REST API 키
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
                "Authorization": f"KakaoAK {self.api_key}",
                "Content-Type": "application/json"
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
            KakaoMapError: API 요청 실패 시
        """
        if not self._client:
            raise KakaoMapError("클라이언트가 초기화되지 않았습니다. async with 문을 사용해주세요.")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await self._client.request(
                method=method,
                url=url,
                params=params,
                json=json_data
            )
            
            # 응답 상태 코드 확인
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                error_message = error_data.get("errorMessage", f"HTTP {response.status_code} 오류")
                error_code = error_data.get("errorType", "UNKNOWN_ERROR")
                raise KakaoMapError(
                    message=error_message,
                    status_code=response.status_code,
                    error_code=error_code
                )
            
            return response.json()
            
        except httpx.TimeoutException:
            raise KakaoMapError("요청 타임아웃이 발생했습니다.")
        except httpx.RequestError as e:
            raise KakaoMapError(f"네트워크 오류: {str(e)}")
        except Exception as e:
            if isinstance(e, KakaoMapError):
                raise
            raise KakaoMapError(f"예상치 못한 오류: {str(e)}")
    
    async def get_car_directions(
        self,
        origin: Coordinate,
        destination: Coordinate,
        waypoints: Optional[List[Coordinate]] = None,
        priority: str = "RECOMMEND",
        car_fuel: str = "GASOLINE",
        car_hipass: bool = False,
        alternatives: bool = False
    ) -> DirectionsResponse:
        """
        자동차 길찾기 요청
        
        Args:
            origin: 출발지 좌표
            destination: 도착지 좌표
            waypoints: 경유지 좌표 목록 (최대 5개)
            priority: 경로 옵션 (RECOMMEND, TIME, DISTANCE)
            car_fuel: 연료 타입 (GASOLINE, DIESEL, LPG)
            car_hipass: 하이패스 사용 여부
            alternatives: 대안 경로 제공 여부
            
        Returns:
            길찾기 결과
            
        Raises:
            KakaoMapError: API 요청 실패 시
            
        Example:
            >>> origin = Coordinate(x=127.108678, y=37.402001)
            >>> dest = Coordinate(x=127.108764, y=37.402127)
            >>> result = await client.get_car_directions(origin, dest)
        """
        # 파라미터 구성
        params = {
            "origin": f"{origin.x},{origin.y}",
            "destination": f"{destination.x},{destination.y}",
            "priority": priority,
            "car_fuel": car_fuel,
            "car_hipass": car_hipass,
            "alternatives": alternatives
        }
        
        # 경유지가 있는 경우 추가
        if waypoints:
            if len(waypoints) > 5:
                raise KakaoMapError("경유지는 최대 5개까지 설정 가능합니다.")
            waypoints_str = "|".join([f"{wp.x},{wp.y}" for wp in waypoints])
            params["waypoints"] = waypoints_str
        
        # API 요청
        data = await self._make_request("GET", "/v1/directions", params=params)
        
        return DirectionsResponse(**data)
    
    async def get_walking_directions(
        self,
        origin: Coordinate,
        destination: Coordinate
    ) -> DirectionsResponse:
        """
        보행자 길찾기 요청
        
        Args:
            origin: 출발지 좌표
            destination: 도착지 좌표
            
        Returns:
            보행자 길찾기 결과
            
        Raises:
            KakaoMapError: API 요청 실패 시
            
        Example:
            >>> origin = Coordinate(x=127.108678, y=37.402001)
            >>> dest = Coordinate(x=127.108764, y=37.402127)
            >>> result = await client.get_walking_directions(origin, dest)
        """
        params = {
            "origin": f"{origin.x},{origin.y}",
            "destination": f"{destination.x},{destination.y}"
        }
        
        # API 요청
        data = await self._make_request("GET", "/v1/walking", params=params)
        
        return DirectionsResponse(**data)
    
    def calculate_distance(self, coord1: Coordinate, coord2: Coordinate) -> float:
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
        lat1_rad = math.radians(coord1.y)
        lon1_rad = math.radians(coord1.x)
        lat2_rad = math.radians(coord2.y)
        lon2_rad = math.radians(coord2.x)
        
        # 차이값 계산
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # 하버사인 공식 적용
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c


# 편의 함수들
async def get_directions(
    api_key: str,
    origin: Coordinate,
    destination: Coordinate,
    waypoints: Optional[List[Coordinate]] = None,
    route_type: str = "car"
) -> DirectionsResponse:
    """
    간편 길찾기 함수
    
    Args:
        api_key: 카카오 API 키
        origin: 출발지
        destination: 도착지
        waypoints: 경유지 목록
        route_type: 경로 타입 ("car" 또는 "walking")
        
    Returns:
        길찾기 결과
    """
    async with KakaoMapClient(api_key=api_key) as client:
        if route_type == "car":
            return await client.get_car_directions(origin, destination, waypoints)
        elif route_type == "walking":
            return await client.get_walking_directions(origin, destination)
        else:
            raise ValueError("route_type은 'car' 또는 'walking'이어야 합니다.")


# 사용 예시
if __name__ == "__main__":

    from dotenv import load_dotenv
    load_dotenv(".env")

    print(os.getenv("KAKAO_MAP_API_KEY"))

    async def example():
        """사용 예시"""
        api_key = os.getenv("KAKAO_MAP_API_KEY")
        
        # 좌표 설정 (강남역 -> 역삼역)
        origin = Coordinate(x=127.027926, y=37.497175)  # 강남역
        destination = Coordinate(x=127.035399, y=37.500489)  # 역삼역
        
        # 클라이언트 사용
        async with KakaoMapClient(api_key=api_key) as client:
            try:
                # 자동차 길찾기
                car_result = await client.get_car_directions(origin, destination)
                print(f"자동차 경로: {car_result.routes[0].result_msg}")
                print(car_result.routes[0])
                
                # 보행자 길찾기
                # walk_result = await client.get_walking_directions(origin, destination)
                # print(f"보행자 경로: {walk_result.routes[0].result_msg}")
                
                # 직선 거리 계산
                distance = client.calculate_distance(origin, destination)
                print(f"직선 거리: {distance:.2f}km")
                
            except KakaoMapError as e:
                raise e
                print(f"카카오 지도 API 오류: {e.message}")
            except Exception as e:
                print(f"예상치 못한 오류: {str(e)}")
    
    # 예시 실행
    asyncio.run(example())
