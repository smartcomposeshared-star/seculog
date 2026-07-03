"use client";
import dynamicImport from "next/dynamic";
import type { MapLocation } from "@/lib/types";

const LoginMap = dynamicImport(() => import("@/components/LoginMap"), { ssr: false });

export default function LoginMapClient({ locations }: { locations: MapLocation[] }) {
  return <LoginMap locations={locations} />;
}
