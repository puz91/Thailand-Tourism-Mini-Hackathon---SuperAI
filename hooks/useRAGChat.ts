"use client";

import { useState, useCallback } from "react";

export interface Message {
  role: "user" | "assistant";
  content: string;
}

export function useRAGChat() {
  const [selectedStation, setSelectedStation] = useState<string>("");
  const [state, setState] = useState({
    messages: [] as Message[],
    isLoading: false,
    error: null as string | null,
  });

  const sendMessage = useCallback(async (userMessage: string) => {
    if (!userMessage.trim() || state.isLoading) return;

    const newUserMessage: Message = { role: "user", content: userMessage };
    setState(prev => ({ 
      ...prev, 
      messages: [...prev.messages, newUserMessage], 
      isLoading: true, 
      error: null 
    }));

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage,
          station: selectedStation,
          history: state.messages.map(m => ({ role: m.role, content: m.content }))
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Server Error");

      const assistantMessage: Message = {
        role: "assistant",
        content: data.response || "มัคจังหาข้อมูลให้แล้ว แต่ระบบขัดข้องเล็กน้อยค่ะ",
      };

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isLoading: false,
      }));
    } catch (err: any) {
      setState(prev => ({ ...prev, isLoading: false, error: err.message }));
    }
  }, [state.messages, state.isLoading, selectedStation]);

  return { ...state, sendMessage, selectedStation, setSelectedStation };
}