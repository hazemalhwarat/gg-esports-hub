"use client";

import { useEffect, useMemo, useState } from "react";
import type { Snapshot, Stream, Match, Tournament } from "@/lib/types";

type Tab = "live" | "streams" | "upcoming" | "results" | "tournaments";

const TABS: { id: Tab; label: string }[] = [
  { id: "live", label: "مباشر الآن" },
  { id: "streams", label: "البثوث" },
  { id: "upcoming", label: "مباريات قادمة" },
  { id: "results", label: "النتائج" },
  { id: "tournaments", label: "البطولات" },
];

export default function Page() {
  const [data, setData] = useState<Snapshot | null>(null);
  const [tab, setTab] = useState<Tab>("live");
  const [priorityOnly, setPriorityOnly] = useState(false);
  const [active, setActive] = useState<Stream | null>(null);
  const [updatedAgo, setUpdatedAgo] = useState<string>("");

  async function load() {
    try {
      const res = await fetch("/data.json?ts=" + Date.now(), { cache: "no-store" });
      const json = (await res.json()) as Snapshot;
      setData(json);
    } catch {
      /* keep last data */
    }
  }

  useEffect(() => {
    load();
    const id = setInterval(load, 60_000); // auto refresh each minute
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    if (!data?.generated_at) return;
    const tick = () => {
      const diff = Math.max(0, (Date.now() - new Date(data.generated_at).getTime()) / 1000);
      setUpdatedAgo(diff < 60 ? `${Math.floor(diff)} ثانية` : `${Math.floor(diff / 60)} دقيقة`);
    };
    tick();
    const id = setInterval(tick, 10_000);
    return () => clearInterval(id);
  }, [data?.generated_at]);

  const streams = data?.streams ?? [];
  const matches = data?.matches ?? [];
  const tournaments = data?.tournaments ?? [];

  const liveMatches = useMemo(
    () => matches.filter((m) => m.status === "live"),
    [matches]
  );
  const finishedMatches = useMemo(
    () => matches.filter((m) => m.status === "finished"),
    [matches]
  );
  const upcomingMatches = useMemo(
    () => matches.filter((m) => m.status === "upcoming"),
    [matches]
  );

  const fp = (arr: any[]) => (priorityOnly ? arr.filter((x) => x.is_priority) : arr);

  return (
    <div className="mx-auto max-w-6xl px-4 py-6">
      <Header updatedAgo={updatedAgo} onRefresh={load} />

      <div className="mt-5 flex flex-wrap items-center gap-2">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`rounded-full px-4 py-1.5 text-sm font-medium transition ${
              tab === t.id
                ? "bg-brand text-white"
                : "bg-panel text-gray-300 hover:bg-panel2"
            }`}
          >
            {t.label}
          </button>
        ))}
        <label className="ms-auto flex cursor-pointer items-center gap-2 text-sm text-gray-300">
          <input
            type="checkbox"
            checked={priorityOnly}
            onChange={(e) => setPriorityOnly(e.target.checked)}
            className="accent-accent"
          />
          الفرق العربية فقط
        </label>
      </div>

      <div className="mt-6">
        {tab === "live" && (
          <div className="space-y-8">
            <Section title="بث مباشر الآن" count={fp(streams).length}>
              <StreamGrid streams={fp(streams)} onOpen={setActive} />
            </Section>
            <Section title="مباريات مباشرة" count={fp(liveMatches).length}>
              <MatchList matches={fp(liveMatches)} />
            </Section>
          </div>
        )}

        {tab === "streams" && (
          <StreamGrid streams={fp(streams)} onOpen={setActive} />
        )}

        {tab === "upcoming" && <MatchList matches={fp(upcomingMatches)} />}

        {tab === "results" && <MatchList matches={fp(finishedMatches)} />}

        {tab === "tournaments" && <TournamentList tournaments={fp(tournaments)} />}
      </div>

      {active && <EmbedModal stream={active} onClose={() => setActive(null)} />}
    </div>
  );
}

function Header({ updatedAgo, onRefresh }: { updatedAgo: string; onRefresh: () => void }) {
  return (
    <div className="flex items-center justify-between border-b border-edge pb-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          GG <span className="text-brand">Esports Hub</span>
        </h1>
        <p className="mt-1 text-sm text-gray-400">
          كل منافسات الايسبورتس في مكان واحد
        </p>
      </div>
      <div className="text-end">
        <button
          onClick={onRefresh}
          className="rounded-lg bg-panel px-3 py-1.5 text-sm text-gray-200 hover:bg-panel2"
        >
          تحديث
        </button>
        {updatedAgo && (
          <p className="mt-1 text-xs text-gray-500">آخر تحديث قبل {updatedAgo}</p>
        )}
      </div>
    </div>
  );
}

function Section({
  title,
  count,
  children,
}: {
  title: string;
  count: number;
  children: React.ReactNode;
}) {
  return (
    <section>
      <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold">
        {title}
        <span className="rounded-full bg-panel2 px-2 py-0.5 text-xs text-gray-400">
          {count}
        </span>
      </h2>
      {children}
    </section>
  );
}

function Empty({ text }: { text: string }) {
  return (
    <div className="rounded-xl border border-dashed border-edge bg-panel/40 p-8 text-center text-sm text-gray-500">
      {text}
    </div>
  );
}

function StreamGrid({
  streams,
  onOpen,
}: {
  streams: Stream[];
  onOpen: (s: Stream) => void;
}) {
  if (!streams.length) return <Empty text="لا يوجد بث مباشر حالياً" />;
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {streams.map((s) => (
        <button
          key={s.id}
          onClick={() => onOpen(s)}
          className={`group overflow-hidden rounded-xl border bg-panel text-start transition hover:-translate-y-0.5 ${
            s.is_priority ? "border-accent/60" : "border-edge"
          }`}
        >
          <div className="relative aspect-video bg-panel2">
            {s.thumbnail ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={s.thumbnail}
                alt={s.channel}
                className="h-full w-full object-cover opacity-90 group-hover:opacity-100"
              />
            ) : null}
            <span className="live-dot absolute top-2 start-2 rounded bg-live px-1.5 py-0.5 text-[10px] font-bold text-white">
              LIVE
            </span>
            <span className="absolute bottom-2 end-2 rounded bg-black/70 px-1.5 py-0.5 text-[11px]">
              👁 {s.viewers.toLocaleString()}
            </span>
            <span className="absolute top-2 end-2 rounded bg-black/70 px-1.5 py-0.5 text-[10px] uppercase">
              {s.platform}
            </span>
          </div>
          <div className="p-3">
            <div className="flex items-center gap-2">
              <p className="truncate text-sm font-semibold">{s.channel}</p>
              {s.is_priority && (
                <span className="rounded bg-accent/20 px-1.5 py-0.5 text-[10px] text-accent">
                  {s.priority_org}
                </span>
              )}
            </div>
            <p className="mt-1 line-clamp-2 text-xs text-gray-400">{s.title}</p>
            {s.game && (
              <p className="mt-1 text-[11px] text-gray-500">{s.game}</p>
            )}
          </div>
        </button>
      ))}
    </div>
  );
}

function MatchList({ matches }: { matches: Match[] }) {
  if (!matches.length) return <Empty text="لا توجد مباريات لعرضها" />;
  return (
    <div className="space-y-2">
      {matches.map((m) => (
        <a
          key={m.id}
          href={m.url}
          target="_blank"
          rel="noreferrer"
          className={`flex items-center gap-3 rounded-xl border bg-panel px-4 py-3 transition hover:bg-panel2 ${
            m.is_priority ? "border-accent/50" : "border-edge"
          }`}
        >
          <span className="w-16 shrink-0 text-[11px] text-gray-500">{m.game}</span>
          <div className="flex flex-1 items-center justify-center gap-3 text-sm">
            <span className="flex-1 text-end font-medium">{m.team_a}</span>
            <span className="rounded bg-panel2 px-2 py-0.5 font-mono text-xs">
              {m.score_a ?? "-"} : {m.score_b ?? "-"}
            </span>
            <span className="flex-1 font-medium">{m.team_b}</span>
          </div>
          <span
            className={`w-14 shrink-0 text-center text-[10px] ${
              m.status === "live" ? "text-live" : "text-gray-500"
            }`}
          >
            {m.status === "live" ? "مباشر" : m.status === "finished" ? "انتهت" : "قادمة"}
          </span>
        </a>
      ))}
    </div>
  );
}

function TournamentList({ tournaments }: { tournaments: Tournament[] }) {
  if (!tournaments.length) return <Empty text="لا توجد بطولات قادمة" />;
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      {tournaments.map((t) => (
        <a
          key={t.id}
          href={t.url}
          target="_blank"
          rel="noreferrer"
          className="rounded-xl border border-edge bg-panel p-4 transition hover:bg-panel2"
        >
          <p className="font-semibold">{t.name}</p>
          <div className="mt-2 flex items-center justify-between text-xs text-gray-400">
            <span>{t.game}</span>
            <span>{formatDate(t.start_time)}</span>
          </div>
        </a>
      ))}
    </div>
  );
}

function EmbedModal({ stream, onClose }: { stream: Stream; onClose: () => void }) {
  const src = useMemo(() => embedUrl(stream), [stream]);
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-4xl overflow-hidden rounded-2xl border border-edge bg-base"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-edge px-4 py-2">
          <p className="text-sm font-semibold">{stream.channel}</p>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            ✕
          </button>
        </div>
        <div className="aspect-video w-full bg-black">
          {src ? (
            <iframe
              src={src}
              className="h-full w-full"
              allow="autoplay; fullscreen"
              allowFullScreen
            />
          ) : (
            <div className="flex h-full items-center justify-center text-sm text-gray-500">
              تعذّر تضمين البث
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ---------- helpers ----------
function embedUrl(s: Stream): string | null {
  if (s.platform === "twitch") {
    const login = s.url.split("/").filter(Boolean).pop();
    const parent =
      typeof window !== "undefined" ? window.location.hostname : "localhost";
    return `https://player.twitch.tv/?channel=${login}&parent=${parent}&autoplay=true`;
  }
  if (s.platform === "youtube") {
    const vid = new URL(s.url).searchParams.get("v");
    return vid ? `https://www.youtube.com/embed/${vid}?autoplay=1` : null;
  }
  if (s.platform === "kick") {
    const slug = s.url.split("/").filter(Boolean).pop();
    return `https://player.kick.com/${slug}`;
  }
  return null;
}

function formatDate(iso: string): string {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleString("ar", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}
