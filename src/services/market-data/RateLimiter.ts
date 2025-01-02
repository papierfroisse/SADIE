interface RateLimitConfig {
  maxRequests: number;
  perMinute: boolean;
}

interface TokenBucket {
  tokens: number;
  lastRefill: number;
}

export class RateLimiter {
  private buckets: Map<string, TokenBucket>;
  private configs: Map<string, RateLimitConfig>;

  constructor(configs: Record<string, RateLimitConfig>) {
    this.buckets = new Map();
    this.configs = new Map(Object.entries(configs));
  }

  private getRefillRate(config: RateLimitConfig): number {
    return config.perMinute ? config.maxRequests / 60000 : config.maxRequests / 3600000;
  }

  private refillBucket(exchange: string): void {
    const bucket = this.buckets.get(exchange);
    const config = this.configs.get(exchange);

    if (!bucket || !config) {
      return;
    }

    const now = Date.now();
    const timePassed = now - bucket.lastRefill;
    const refillRate = this.getRefillRate(config);
    const tokensToAdd = timePassed * refillRate;

    bucket.tokens = Math.min(config.maxRequests, bucket.tokens + tokensToAdd);
    bucket.lastRefill = now;
  }

  public async waitForToken(exchange: string): Promise<void> {
    const config = this.configs.get(exchange);
    if (!config) {
      throw new Error(`No rate limit configuration for exchange: ${exchange}`);
    }

    if (!this.buckets.has(exchange)) {
      this.buckets.set(exchange, {
        tokens: config.maxRequests,
        lastRefill: Date.now()
      });
    }

    const bucket = this.buckets.get(exchange)!;
    this.refillBucket(exchange);

    if (bucket.tokens < 1) {
      const refillRate = this.getRefillRate(config);
      const waitTime = Math.ceil((1 - bucket.tokens) / refillRate);
      await new Promise(resolve => setTimeout(resolve, waitTime));
      this.refillBucket(exchange);
    }

    bucket.tokens -= 1;
  }
} 