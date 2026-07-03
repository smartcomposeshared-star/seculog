import SummaryCards from "@/components/SummaryCards";

export const dynamic = "force-dynamic";

export default function OverviewPage() {
  return (
    <div>
      <h1 className="text-xl font-bold mb-4">Overview</h1>
      <SummaryCards />
    </div>
  );
}
