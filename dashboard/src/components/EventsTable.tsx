import type { LoginEvent } from "@/lib/types";

export default function EventsTable({ events }: { events: LoginEvent[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-gray-400 border-b border-gray-800 text-left">
            <th className="py-2 pr-6 font-medium">Time</th>
            <th className="py-2 pr-6 font-medium">Username</th>
            <th className="py-2 pr-6 font-medium">IP Address</th>
            <th className="py-2 pr-6 font-medium">Country</th>
            <th className="py-2 font-medium">Result</th>
          </tr>
        </thead>
        <tbody>
          {events.map((e) => (
            <tr
              key={e.id}
              className="border-b border-gray-900 hover:bg-gray-900 transition-colors"
            >
              <td className="py-2 pr-6 font-mono text-gray-400 text-xs">
                {new Date(e.timestamp).toLocaleString()}
              </td>
              <td className="py-2 pr-6">{e.username}</td>
              <td className="py-2 pr-6 font-mono text-xs">{e.ip_address}</td>
              <td className="py-2 pr-6 text-gray-300">{e.country ?? "—"}</td>
              <td className="py-2">
                {e.success ? (
                  <span className="text-green-400 font-bold">✓ Success</span>
                ) : (
                  <span className="text-red-400 font-bold">✗ Failed</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {events.length === 0 && (
        <p className="text-gray-500 py-4">No events yet.</p>
      )}
    </div>
  );
}
