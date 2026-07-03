import { supabase } from "@/lib/supabase";

export default async function Page() {
  const { data, error } = await supabase.from("login_events").select("id").limit(1);
  return <pre className="p-4">{JSON.stringify({ data, error }, null, 2)}</pre>;
}
