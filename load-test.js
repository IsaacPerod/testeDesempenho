import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 50,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(95)<500'],
  },
};

const endpoints = ['/', '/json', '/file/1mb.bin', '/file/10mb.bin', '/file/100mb.bin'];

export default function () {
  for (let endpoint of endpoints) {
    let resHttp1 = http.get(`http://127.0.0.1:5000${endpoint}`);
    check(resHttp1, { 'HTTP/1.1 status is 200': (r) => r.status === 200 });

    let resHttp3 = http.get(`https://localhost:4434${endpoint}`, { insecureSkipTLSVerify: true });
    check(resHttp3, { 'HTTP/3 status is 200': (r) => r.status === 200 });

    sleep(1);
  }
}