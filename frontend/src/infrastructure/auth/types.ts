export interface Account {
  id: string;
  email: string;
  role: 'parent' | 'administrator';
}

export interface ChildProfile {
  id: string;
  account_id: string;
  display_name: string;
  created_at: string;
}
