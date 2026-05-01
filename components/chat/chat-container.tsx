"use client"

import { useRef, useEffect, useState, useCallback } from "react"
import { ChatMessage, type Message } from "./chat-message"
import { ChatInput } from "./chat-input"
import { TypingIndicator } from "./typing-indicator"
import { StationSelector, stations } from "./station-selector"
import { ScrollArea } from "@/components/ui/scroll-area"
import { MessageSquare } from "lucide-react"

export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedStation, setSelectedStation] = useState<string>("")
  const scrollRef = useRef<HTMLDivElement>(null)

  // Get station name for display
  const stationName = stations.find((s) => s.id === selectedStation)?.nameEn

  // Auto scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading, scrollToBottom])

  const sendMessage = async (content: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content,
    }

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: content, station: selectedStation }),
      })

      if (!response.ok) {
        throw new Error("Failed to send message")
      }

      const data = await response.json()

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.message,
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch {
      setError("Something went wrong. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex h-screen flex-col bg-background">
      {/* Header */}
      <header className="flex items-center justify-between border-b px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="flex size-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <MessageSquare className="size-5" />
          </div>
          <div>
            <h1 className="text-lg font-semibold">Bangkok Travel AI</h1>
            <p className="text-sm text-muted-foreground">
              {stationName ? `${stationName} Station` : "Select a station to start chatting"}
            </p>
          </div>
        </div>
        <StationSelector
          value={selectedStation}
          onValueChange={setSelectedStation}
        />
      </header>

      {/* Messages */}
      <ScrollArea className="flex-1">
        <div className="mx-auto max-w-3xl">
          {messages.length === 0 ? (
            <div className="flex h-[calc(100vh-200px)] flex-col items-center justify-center px-4 text-center">
              <div className="flex size-16 items-center justify-center rounded-full bg-muted">
                <MessageSquare className="size-8 text-muted-foreground" />
              </div>
              <h2 className="mt-4 text-xl font-semibold">
                Discover places near your station
              </h2>
              <p className="mt-2 text-muted-foreground text-sm">
                Ask about places near BTS or MRT stations:
              </p>

              <ul className="mt-2 text-sm text-muted-foreground space-y-1 text-left">
                <li>• Cafés near BTS Siam</li>
                <li>• Things to do near MRT Chatuchak</li>
                <li>• Best restaurants around Asok</li>
              </ul>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {isLoading && <TypingIndicator />}
              {error && (
                <div className="px-4 py-3 text-center text-sm text-destructive">
                  {error}
                </div>
              )}
            </>
          )}
          <div ref={scrollRef} />
        </div>
      </ScrollArea>

      {/* Input */}
      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </div>
  )
}
