"use client"

import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Train } from "lucide-react"

export interface Station {
  id: string
  name: string
  nameEn: string
  line: string
  lineEn: string
}

const stations: Station[] = [
  // BTS Sukhumvit Line
  { id: "bts-siam", name: "สยาม", nameEn: "Siam", line: "BTS สายสุขุมวิท", lineEn: "BTS Sukhumvit Line" },
  { id: "bts-asok", name: "อโศก", nameEn: "Asok", line: "BTS สายสุขุมวิท", lineEn: "BTS Sukhumvit Line" },
  { id: "bts-phrom-phong", name: "พร้อมพงษ์", nameEn: "Phrom Phong", line: "BTS สายสุขุมวิท", lineEn: "BTS Sukhumvit Line" },
  { id: "bts-thong-lo", name: "ทองหล่อ", nameEn: "Thong Lo", line: "BTS สายสุขุมวิท", lineEn: "BTS Sukhumvit Line" },
  { id: "bts-ekkamai", name: "เอกมัย", nameEn: "Ekkamai", line: "BTS สายสุขุมวิท", lineEn: "BTS Sukhumvit Line" },
  // BTS Silom Line
  { id: "bts-sala-daeng", name: "ศาลาแดง", nameEn: "Sala Daeng", line: "BTS สายสีลม", lineEn: "BTS Silom Line" },
  { id: "bts-chong-nonsi", name: "ช่องนนทรี", nameEn: "Chong Nonsi", line: "BTS สายสีลม", lineEn: "BTS Silom Line" },
  { id: "bts-surasak", name: "สุรศักดิ์", nameEn: "Surasak", line: "BTS สายสีลม", lineEn: "BTS Silom Line" },
  // MRT Blue Line
  { id: "mrt-sukhumvit", name: "สุขุมวิท", nameEn: "Sukhumvit", line: "MRT สายสีน้ำเงิน", lineEn: "MRT Blue Line" },
  { id: "mrt-petchaburi", name: "เพชรบุรี", nameEn: "Petchaburi", line: "MRT สายสีน้ำเงิน", lineEn: "MRT Blue Line" },
  { id: "mrt-phahon-yothin", name: "พหลโยธิน", nameEn: "Phahon Yothin", line: "MRT สายสีน้ำเงิน", lineEn: "MRT Blue Line" },
  { id: "mrt-lat-phrao", name: "ลาดพร้าว", nameEn: "Lat Phrao", line: "MRT สายสีน้ำเงิน", lineEn: "MRT Blue Line" },
  { id: "mrt-chatuchak", name: "จตุจักร", nameEn: "Chatuchak Park", line: "MRT สายสีน้ำเงิน", lineEn: "MRT Blue Line" },
]

// Group stations by line
const groupedStations = stations.reduce(
  (acc, station) => {
    if (!acc[station.line]) {
      acc[station.line] = []
    }
    acc[station.line].push(station)
    return acc
  },
  {} as Record<string, Station[]>
)

interface StationSelectorProps {
  value: string
  onValueChange: (value: string) => void
}

export function StationSelector({ value, onValueChange }: StationSelectorProps) {
  const selectedStation = stations.find((s) => s.id === value)

  return (
    <Select value={value} onValueChange={onValueChange}>
      <SelectTrigger className="w-[220px]">
        <Train className="size-4 text-muted-foreground" />
        <SelectValue placeholder="Select Station">
          {selectedStation ? `${selectedStation.name} ${selectedStation.nameEn}` : "Select Station"}
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        {Object.entries(groupedStations).map(([line, lineStations]) => (
          <SelectGroup key={line}>
            <SelectLabel className="flex flex-col">
              {/* <span>{line}</span> */}
              <span className="text-xs font-normal text-muted-foreground">{lineStations[0]?.lineEn}</span>
            </SelectLabel>
            {lineStations.map((station) => (
              <SelectItem key={station.id} value={station.id}>
                <span className="flex items-center gap-2">
                  <span>{station.name}</span>
                  <span className="text-muted-foreground">{station.nameEn}</span>
                </span>
              </SelectItem>
            ))}
          </SelectGroup>
        ))}
      </SelectContent>
    </Select>
  )
}

export { stations }
