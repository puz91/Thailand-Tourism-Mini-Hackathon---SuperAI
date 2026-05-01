import { NextResponse } from "next/server"

export async function POST(request: Request) {
  try {
    const { message, station } = await request.json()

    if (!message || typeof message !== "string") {
      return NextResponse.json(
        { error: "Message is required" },
        { status: 400 }
      )
    }

    // Simulate AI response with a delay
    // Replace this with your actual AI integration
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // Echo response for demonstration
    // In production, integrate with your AI provider here
    const stationInfo = station ? `\n\nสถานีที่เลือก: ${station}` : ""
    const response = `ได้รับข้อความของคุณ: "${message}"${stationInfo}\n\nนี่คือการตอบกลับตัวอย่าง สามารถเชื่อมต่อ AI provider จริงได้ใน API route นี้`

    return NextResponse.json({ message: response })
  } catch {
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
}
