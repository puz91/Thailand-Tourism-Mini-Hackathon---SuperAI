"use client"

import { useRef, useEffect, useCallback } from "react"
import { ChatMessage } from "./chat-message"
import { ChatInput } from "./chat-input"
import { TypingIndicator } from "./typing-indicator"
import { StationSelector, stations } from "./station-selector"
import { ScrollArea } from "@/components/ui/scroll-area"
import { MessageSquare } from "lucide-react"
import { useRAGChat } from "@/hooks/useRAGChat" // ✅ เรียกใช้ Hook

export function ChatContainer() {
  // ✅ ดึงทุกอย่างจาก Hook ที่เดียว
  const { messages, isLoading, error, sendMessage, selectedStation, setSelectedStation } = useRAGChat();
  
  const scrollRef = useRef<HTMLDivElement>(null)
  const stationName = stations.find((s) => s.id === selectedStation)?.name

  const scrollToBottom = useCallback(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading, scrollToBottom])

  return (
    <div className="flex h-screen flex-col bg-background">
      <header className="flex items-center justify-between border-b px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="flex size-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <MessageSquare className="size-5" />
          </div>
          <div>
            <h1 className="text-lg font-semibold">Muek-Jung AI</h1>
            <p className="text-sm text-muted-foreground">
              {stationName ? `สถานี${stationName}` : "เลือกสถานีเพื่อเริ่มคุย"}
            </p>
          </div>
        </div>
        <StationSelector value={selectedStation} onValueChange={setSelectedStation} />
      </header>

      <ScrollArea className="flex-1">
        <div className="mx-auto max-w-3xl">
          {messages.length === 0 ? (
            <div className="flex h-[calc(100vh-200px)] flex-col items-center justify-center px-4 text-center">
              <h2 className="text-xl font-semibold">สวัสดีค่ะ! มัคจังพร้อมแล้ว</h2>
              <p className="text-muted-foreground">ลองทักทาย หรือถามที่เที่ยวได้เลยนะคะ</p>
            </div>
          ) : (
            <>
              {messages.map((msg, i) => (
                // ✅ ส่ง msg เข้าไป (ChatMessage ต้องรองรับ role/content)
                <ChatMessage key={i} message={msg as any} /> 
              ))}
              {isLoading && <TypingIndicator />}
              {error && <div className="p-4 text-center text-destructive">{error}</div>}
            </>
          )}
          <div ref={scrollRef} />
        </div>
      </ScrollArea>

      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </div>
  )
}