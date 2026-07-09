import { supabase } from "@/lib/supabase";

const sgtDateFormatter = new Intl.DateTimeFormat("en-CA", {
  timeZone: "Asia/Singapore",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
});

export default async function SummaryCards() {
  const todaySgt = sgtDateFormatter.format(new Date());
  const todayStart = new Date(`${todaySgt}T00:00:00+08:00`);

  const [
    { count: loginCount },
    { count: alertCount },
    { data: alertsByType },
  ] = await Promise.all([
    supabase
      .from("login_events")
      .select("*", { count: "exact", head: true })
      .gte("timestamp", todayStart.toISOString()),
    supabase.from("alerts").select("*", { count: "exact", head: true }),
    supabase.from("alerts").select("rule_type"),
  ]);

  const typeCounts = (alertsByType ?? []).reduce<Record<string, number>>(
    (acc, row) => ({ ...acc, [row.rule_type]: (acc[row.rule_type] ?? 0) + 1 }),
    {}
  );

  const ruleLabel: Record<string, string> = {
    brute_force: "Brute Force",
    impossible_travel: "Impossible Travel",
    known_bad_ip: "Known Bad IP",
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
      <div className="bg-gray-900 rounded-lg p-4">
        <p className="text-gray-400 text-sm mb-1">Logins Today</p>
        <p className="text-3xl font-bold text-white">{loginCount ?? 0}</p>
      </div>
      <div className="bg-gray-900 rounded-lg p-4">
        <p className="text-gray-400 text-sm mb-1">Total Alerts</p>
        <p className="text-3xl font-bold text-red-400">{alertCount ?? 0}</p>
      </div>
      <div className="bg-gray-900 rounded-lg p-4">
        <p className="text-gray-400 text-sm mb-1">Alerts by Type</p>
        {Object.keys(typeCounts).length === 0 && (
          <p className="text-gray-500 text-sm">No alerts yet</p>
        )}
        {Object.entries(typeCounts).map(([type, count]) => (
          <p key={type} className="text-sm">
            <span className="text-gray-300">{ruleLabel[type] ?? type}</span>
            <span className="text-gray-500 ml-1">— {count}</span>
          </p>
        ))}
      </div>
    </div>
  );
}
