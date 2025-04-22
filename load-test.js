import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 10, // Reduzir para 10 VUs para depuração
  duration: '10s', // Reduzir para 10s
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<500'],
  },
};

const endpoints = ['/', '/json', '/file/1mb.bin'];

export default function () {
  endpoints.forEach(endpoint => {
    const res = http.get(`http://localhost:5000${endpoint}`);
    console.log(`HTTP/1.1 request to ${endpoint}: status=${res.status}, error=${res.error || 'no error'}, body=${res.body || 'no body'}`);
    check(res, { 'HTTP/1.1 status is 200': (r) => r.status === 200 });
  });

  // Comentar HTTP/3 temporariamente para isolar o problema
  endpoints.forEach(endpoint => {
    const res = http.get(`https://localhost:4433${endpoint}`, {
      insecureSkipTLSVerify: true,
      alpnProtocols: ['h3'],
    });
    console.log(`HTTP/3 request to ${endpoint}: status=${res.status}, error=${res.error || 'no error'}, body=${res.body || 'no body'}`);
    check(res, { 'HTTP/3 status is 200': (r) => r.status === 200 });
  });
}