import { supabase } from "@/lib/supabase";
import EventsTable from "@/components/EventsTable";

export const dynamic = "force-dynamic";

export default async function EventsPage() {
  const { data: events } = await supabase
    .from("login_events")
    .select("*")
    .order("timestamp", { ascending: false })
    .limit(200);

  return (
    <div>
      <h1 className="text-xl font-bold mb-2">All Login Events</h1>
      <p className="text-gray-400 text-sm mb-4">
        Showing the {(events ?? []).length} most recent events.
      </p>
      <EventsTable events={events ?? []} />
    </div>
  );
}
