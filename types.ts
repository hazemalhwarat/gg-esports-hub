export interface Stream {
  id: string;
  platform: "twitch" | "youtube" | "kick";
  channel: string;
  title: string;
  game: string;
  viewers: number;
  url: string;
  thumbnail: string;
  is_priority: boolean;
  priority_org: string | null;
  started_at: string;
}

export interface Match {
  id: string;
  game: string;
  tournament: string;
  team_a: string;
  team_b: string;
  score_a: number | null;
  score_b: number | null;
  status: "upcoming" | "live" | "finished";
  start_time: string;
  source: string;
  url: string;
  tier: string;
  is_priority: boolean;
  priority_org: string | null;
}

export interface Tournament {
  id: string;
  name: string;
  game: string;
  status: string;
  start_time: string;
  end_time: string;
  source: string;
  url: string;
  prize: string;
}

export interface Snapshot {
  generated_at: string;
  streams: Stream[];
  matches: Match[];
  tournaments: Tournament[];
}
