"use client";

import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import type { MapLocation } from "@/lib/types";

export default function LoginMap({ locations }: { locations: MapLocation[] }) {
  return (
    <MapContainer
      center={[20, 0]}
      zoom={2}
      style={{ height: "300px", width: "100%" }}
      scrollWheelZoom={false}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      />
      {locations.map((loc, i) => (
        <CircleMarker
          key={i}
          center={[loc.lat, loc.lon]}
          radius={6}
          pathOptions={{
            color: loc.suspicious ? "#ef4444" : "#3b82f6",
            fillColor: loc.suspicious ? "#ef4444" : "#3b82f6",
            fillOpacity: 0.7,
          }}
        >
          <Popup>
            <span style={{ fontFamily: "monospace", fontSize: "13px" }}>
              {loc.username} — {loc.country ?? "Unknown"}
            </span>
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
