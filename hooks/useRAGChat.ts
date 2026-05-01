"use client";

import { useState, useCallback } from "react";

export interface Message {
  role: "user" | "assistant";
  content: string;
}

export interface PlaceResult {
  id: number;
  name: string;
  category: string;
  station: string;
  line: string;
  exit: string;
  distance_meters: number;
  walk_minutes: number;
  details: string;
  highlight: string;
  open_hours: string;
  price: string;
  tags: string[];
}

export interface ChatState {
  messages: Message[];
  places: PlaceResult[];
  isLoading: boolean;
  error: string | null;
}

export function useRAGChat() {
  const [state, setState] = useState<ChatState>({
    messages: [],
    places: [],
    isLoading: false,
    error: null,
  });

  const sendMessage = useCallback(async (userMessage: string) => {
    if (!userMessage.trim() || state.isLoading) return;

    const newUserMessage: Message = { role: "user", content: userMessage };
    const updatedHistory = [...state.messages, newUserMessage];

    setState((prev) => ({
      ...prev,
      messages: updatedHistory,
      places: [],
      isLoading: true,
      error: null,
    }));

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage,
          // ✅ กรอง History ให้สะอาด: เอาเฉพาะข้อความที่มีเนื้อหาจริงๆ และ Trim หัวท้าย
          history: state.messages
            .filter(msg => msg.content && msg.content.trim() !== "")
            .map(msg => ({
              role: msg.role,
              content: msg.content.trim()
            })),
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `HTTP ${res.status}`);
      }

      const data = await res.json();
      
      // ✅ ป้องกันกรณี AI ตอบกลับมาเป็นค่าว่าง
      const assistantMessage: Message = {
        role: "assistant",
        content: data.response || "มัคจังหาข้อมูลให้แล้ว แต่ดูเหมือนระบบขัดข้องเล็กน้อย ลองถามใหม่อีกครั้งนะคะ",
      };

      setState((prev) => ({
        ...prev,
        messages: [...updatedHistory, assistantMessage],
        places: data.places_found || [],
        isLoading: false,
      }));
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "เกิดข้อผิดพลาด";
      setState((prev) => ({
        ...prev,
        messages: [
          ...updatedHistory,
          {
            role: "assistant",
            content: `⚠️ ขออภัยค่ะ เกิดข้อผิดพลาด: ${errorMsg}`,
          },
        ],
        isLoading: false,
        error: errorMsg,
      }));
    }
  }, [state]);

  const clearChat = useCallback(() => {
    setState({ messages: [], places: [], isLoading: false, error: null });
  }, []);

  return { ...state, sendMessage, clearChat };
}