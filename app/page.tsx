// ✅ ต้องมีปีกกา { } เพราะเราใช้ export function (Named Export)
import { ChatContainer } from "@/components/chat/chat-container"

export default function Home() {
  return (
    <main>
      <ChatContainer />
    </main>
  )
}