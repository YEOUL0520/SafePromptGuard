/** 동작 확인용 입력 예시 — 검사 버튼 누르기 전에 불러오기 */

export const SAMPLES = [
  {
    id: 'spring-db',
    label: '① Spring Boot + DB (위험 높음)',
    description: 'DB URL, 비밀번호, AWS Key, 내부 도메인',
    text: `Spring Boot DB 연결 오류 봐줘.

spring.datasource.url=jdbc:mysql://prod-db.company.internal:3306/customer_payment
spring.datasource.username=admin
spring.datasource.password=Qwer1234!
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE

고객 결제 테이블(customer_payment)에서 timeout이 발생하고 있어.
운영(production) 환경이고 내부망 DB야.`,
  },
  {
    id: 'env-file',
    label: '② .env 설정 파일',
    description: 'API Key, Secret, DB 호스트',
    text: `# .env — 로컬에서 복사한 설정
DB_HOST=prod-db.company.internal
DB_USER=payment_admin
DB_PASSWORD=SuperSecret!2024
SECRET_KEY=sk-live-abc123xyz789secretkey
STRIPE_API_KEY=sk_test_51HxK9exampleSecretKey
REDIS_URL=redis://10.0.12.45:6379/0
ADMIN_EMAIL=devops@company.internal`,
  },
  {
    id: 'error-log',
    label: '③ 에러 로그 + JWT',
    description: 'JWT, 내부 IP, Bearer 토큰',
    text: `2026-05-16 14:32:01 ERROR [payment-service] Connection refused
  host=192.168.10.55 port=5432 database=customer_billing
  user=svc_payment

Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

Caused by: timeout after 30000ms contacting internal-api.company.corp`,
  },
  {
    id: 'trade-secret',
    label: '④ 영업비밀 문맥 (규칙+Gemma)',
    description: '비밀번호 패턴 없음 · 알고리즘·고객·계약',
    text: `우리 회사 추천 알고리즘은 사용자 구매 이력과 내부 등급 점수를 조합해 산출한다.

VIP 고객사는 A전자, B물산, C리테일이며 다음 분기 계약 단가는 건당 1,200원, 980원, 1,050원이다.

내부 결제 모듈의 재시도 로직 결함 때문에 production 장애가 발생했다.
고객사 담당자 연락처: kim.manager@partner.co.kr / 010-9876-5432`,
  },
  {
    id: 'python-code',
    label: '⑤ Python 코드 스니펫',
    description: '하드코딩된 credential',
    text: `import requests

API_KEY = "sk-proj-9f8e7d6c5b4a3210example"
BASE_URL = "https://internal-gateway.company.internal/api/v2"

def sync_customer_payment(customer_id: str):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    # customer_payment 테이블과 연동
    return requests.post(f"{BASE_URL}/payments", headers=headers, json={"id": customer_id})`,
  },
  {
    id: 'safe-low',
    label: '⑥ 비교용 · 상대적 안전',
    description: '위험도 낮음 확인용',
    text: `React에서 useEffect 의존성 배열을 빼먹으면 무한 렌더가 납니다.

function UserList() {
  const [users, setUsers] = useState([]);
  useEffect(() => {
    fetch('/api/public/users').then(r => r.json()).then(setUsers);
  }, []);
}

이 패턴에서 왜 무한 루프가 생기는지, 수정 예시를 알려주세요.`,
  },
]

export const DEFAULT_SAMPLE_ID = 'spring-db'
