export type Opportunity = {
  account: string;
  product: string;
  score: number;
  opportunity_type?: 'cross_sell' | 'upsell' | 'prospect' | 'churn_risk';
  explanation: string;
  next_action?: string;
  segment?: string;
  territory?: string;
};

export type Summary = {
  top_opportunities: Opportunity[];
  top_risks: Opportunity[];
};

export async function fetchOpportunities(
  userId: string,
  opportunityType: 'cross_sell' | 'upsell' | 'prospect',
  topN: number = 5,
  filters?: { productId?: string; segment?: string; territory?: string; accountId?: string }
): Promise<Opportunity[]> {
  const params = new URLSearchParams({
    user_id: userId,
    opportunity_type: opportunityType,
    top_n: topN.toString(),
  });
  if (filters?.productId) params.append('product_id', filters.productId);
  if (filters?.segment) params.append('segment', filters.segment);
  if (filters?.territory) params.append('territory', filters.territory);
  if (filters?.accountId) params.append('account_id', filters.accountId);
  const response = await fetch(`/api/opportunities?${params.toString()}`);
  if (!response.ok) {
    throw new Error('Failed to fetch opportunities');
  }
  return response.json();
}

export async function fetchChurnRisk(
  userId: string,
  topN: number = 5,
  filters?: { segment?: string; territory?: string }
): Promise<Opportunity[]> {
  const params = new URLSearchParams({
    user_id: userId,
    top_n: topN.toString(),
  });
  if (filters?.segment) params.append('segment', filters.segment);
  if (filters?.territory) params.append('territory', filters.territory);
  const response = await fetch(`/api/churn_risk?${params.toString()}`);
  if (!response.ok) {
    throw new Error('Failed to fetch churn risk accounts');
  }
  return response.json();
}

export async function fetchSummary(userId: string): Promise<Summary> {
  const params = new URLSearchParams({ user_id: userId });
  const response = await fetch(`/api/summary?${params.toString()}`);
  if (!response.ok) {
    throw new Error('Failed to fetch summary');
  }
  return response.json();
}

export async function fetchPersonalizedPitch(accountId: string, productId: string): Promise<{ account: string; product: string; pitch: string }> {
  const params = new URLSearchParams({ account_id: accountId, product_id: productId });
  const response = await fetch(`/api/pitch?${params.toString()}`);
  if (!response.ok) {
    throw new Error('Failed to fetch personalized pitch');
  }
  return response.json();
} 