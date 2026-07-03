import dynamicImport from "next/dynamic";
import { supabase } from "@/lib/supabase";
import SummaryCards from "@/components/SummaryCards";
import AlertFeed from "@/components/AlertFeed";
import type { MapLocation } from "@/lib/types";

export const dynamic = "force-dynamic";

const LoginMap = dynamicImport(() => import("@/components/LoginMap"), { ssr: false });

export default async function OverviewPage() {
  const [{ data: events }, { data: alertRows }] = await Promise.all([
    supabase
      .from("login_events")
      .select("id, lat, lon, username, country")
      .not("lat", "is", null)
      .order("timestamp", { ascending: false })
      .limit(100),
    supabase.from("alerts").select("login_event_id"),
  ]);

  const suspiciousIds = new Set(
    (alertRows ?? []).map((a) => a.login_event_id)
  );

  const locations: MapLocation[] = (events ?? []).map((e) => ({
    lat: e.lat as number,
    lon: e.lon as number,
    username: e.username,
    country: e.country,
    suspicious: suspiciousIds.has(e.id),
  }));

  return (
    <div>
      <h1 className="text-xl font-bold mb-4">Overview</h1>
      <SummaryCards />
      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-3">Login Locations</h2>
        <div className="rounded-lg overflow-hidden border border-gray-800">
          <LoginMap locations={locations} />
        </div>
      </div>
      <AlertFeed />
    </div>
  );
}
