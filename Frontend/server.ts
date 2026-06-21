import express from "express";
import path from "path";
import dotenv from "dotenv";
import { GoogleGenAI } from "@google/genai";
import { createServer as createViteServer } from "vite";

dotenv.config();

const app = express();
app.use(express.json());

const PORT = 3000;

// Initialize GoogleGenAI SDK on the server with user-agent for telemetry
const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY,
  httpOptions: {
    headers: {
      'User-Agent': 'aistudio-build',
    }
  }
});

// Real AI Chat Endpoint for Busynes Copilot
app.post("/api/chat", async (req, res) => {
  try {
    const { message } = req.body;
    if (!message) {
      return res.status(400).json({ error: "Message is required" });
    }

    const systemInstruction = `You are Busynes Copilot, a helpful real-time AI financial planning assistant for UK sports venue operators, stadium CPAs, and sports club managers running the Busynes SaaS.

Core Context & Persona Rules:
- Under no circumstances make up or simulate a terminal window or server logs inside your text.
- Be highly helpful, supportive, professional, and clear.
- All monetary operations and responses MUST strictly be formatted in UK Pound Sterling (£), using British spelling standards (e.g. categorisation, optimisation, general overheads, colour).
- When asked about transactions or invoices, mention that the user can import, inspect, edit, and verify receipts directly inside our secure "Invoice Vault" page.
- Talk about our actual UK-centric integrations: British Gas Commercial, Club Catering Ltd, and Cloudflare Inc.
- If asked about multi-currency support, explain that the platform is currently fully optimized for UK Sterling (£) as the preferred currency to maximize simplicity and precision under current HMRC guidelines, and other currencies are scheduled for future billing releases.
- Answer user queries directly with high-quality financial guidance customized for sports venue and stadium overhead management.`;

    // Generate responsive content from Gemini
    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: message,
      config: {
        systemInstruction,
        temperature: 0.7,
      }
    });

    res.json({ reply: response.text });
  } catch (error: any) {
    console.error("Gemini API Error:", error);
    res.status(500).json({ error: "Something went wrong. Please check your GEMINI_API_KEY." });
  }
});

async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    // Serve html pages properly
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
