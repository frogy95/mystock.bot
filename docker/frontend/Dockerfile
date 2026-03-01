# Next.js 프론트엔드 Dockerfile
# Node.js 22 Alpine 이미지 사용

FROM node:22-alpine

WORKDIR /app

# 의존성 파일 먼저 복사 (Docker 레이어 캐싱 활용)
COPY frontend/package*.json ./
RUN npm ci

# 소스 코드 복사 (frontend/ 디렉토리 내용)
COPY frontend/ .

# Next.js 개발 서버 실행 (모든 인터페이스에서 수신)
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]
