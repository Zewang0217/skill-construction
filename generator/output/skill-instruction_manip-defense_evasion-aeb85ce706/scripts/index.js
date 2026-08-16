// Main entry point for npm package
const axios = require('axios');

class APIClientWrapper {
  constructor(baseUrl, apiKey) {
    this.client = axios.create({
      baseURL: baseUrl,
      headers: apiKey ? { 'Authorization': `Bearer ${apiKey}` } : {}
    });
  }

  request(method, path, data) {
    return this.client.request({ method, url: path, data });
  }
}

module.exports = { APIClientWrapper };