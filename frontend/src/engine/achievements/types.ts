export interface Achievement {
  key: string;
  category: string;
  title: string;
  description: string;
  hidden: boolean;
  icon_path: string;
  unlocked_at: string | null;
}

export interface PlayerAchievement extends Achievement {
  avatar_id: string | null;
}
