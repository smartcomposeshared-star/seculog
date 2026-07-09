import { supabase } from "@/lib/supabase";
import { formatDateTime } from "@/lib/format";
import type { Alert } from "@/lib/types";

export default async function AlertFeed() {
  const { data: alerts } = await supabase
    .from("alerts")
    .select("*, login_events(ip_address)")
    .order("timestamp", { ascending: false })
    .limit(50);

  return (
    <div className="mb-6">
      <h2 className="text-lg font-semibold mb-3">Alert Feed</h2>
      {(alerts ?? []).length === 0 && (
        <p className="text-gray-500">No alerts yet.</p>
      )}
      <div className="space-y-2">
        {(alerts ?? []).map((alert: Alert) => (
          <div
            key={alert.id}
            className={`rounded border px-4 py-3 ${
              alert.severity === "high"
                ? "bg-red-950 border-red-800"
                : "bg-yellow-950 border-yellow-800"
            }`}
          >
            <div className="flex justify-between items-start">
              <span className="font-mono text-gray-300 text-sm">
                {formatDateTime(alert.timestamp)}
              </span>
              <span
                className={`text-xs font-bold uppercase tracking-wide ${
                  alert.severity === "high" ? "text-red-400" : "text-yellow-400"
                }`}
              >
                {alert.severity}
              </span>
            </div>
            <p className="mt-1">
              <span className="text-blue-300 font-medium">
                {alert.rule_type.replace(/_/g, " ")}
              </span>
              <span className="text-gray-400 ml-2 text-sm">
                — {alert.username}
                {alert.login_events?.ip_address && ` / ${alert.login_events.ip_address}`}
              </span>
            </p>
            <p className="text-gray-300 text-sm mt-1">{alert.details}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
