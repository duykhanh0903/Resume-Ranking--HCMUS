import json
import os
from typing import TypedDict, Annotated, List, Union
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from src.engine.tools.sbert_tools import verify_semantic_similarity, deep_scan_raw_text
from src.engine.prompts.agent_prompts import RECRUITER_SYSTEM_PROMPT

# Định nghĩa trạng thái của Agent (State)
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]

class RecruitAIAgent:
    def __init__(self, api_key: str):
        # 1. Khởi tạo LLM
        self.llm = ChatGroq(
            temperature=0, 
            model_name="llama-3.3-70b-versatile", 
            groq_api_key=api_key
        )
        
        # 2. Khởi tạo Tools
        self.tools = [verify_semantic_similarity, deep_scan_raw_text]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # 3. Xây dựng đồ thị (StateGraph) - Thay thế cho create_react_agent
        workflow = StateGraph(AgentState)

        # Định nghĩa các nút (Nodes)
        workflow.add_node("agent", self._call_model)
        workflow.add_node("action", ToolNode(self.tools))

        # Thiết lập luồng chạy
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "action",
                "end": END
            }
        )
        workflow.add_edge("action", "agent")

        self.agent = workflow.compile()

    def _should_continue(self, state: AgentState):
        last_message = state["messages"][-1]
        if not last_message.tool_calls:
            return "end"
        return "continue"

    def _call_model(self, state: AgentState):
        # Chèn System Prompt vào đầu luồng suy luận
        messages = [HumanMessage(content=RECRUITER_SYSTEM_PROMPT)] + state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}

    async def run_analysis(self, jd: dict, resume: dict, raw_text: str) -> dict:
        input_text = f"JD: {json.dumps(jd, ensure_ascii=False)}\nResume JSON: {json.dumps(resume, ensure_ascii=False)}\nRaw Text: {raw_text}"
        
        try:
            inputs = {"messages": [HumanMessage(content=input_text)]}
            response = await self.agent.ainvoke(inputs)
            
            final_message = response["messages"][-1].content
            
            # Làm sạch JSON đầu ra
            cleaned_text = final_message.strip()
            if "```json" in cleaned_text:
                cleaned_text = cleaned_text.split("```json")[1].split("```")[0]
            
            return json.loads(cleaned_text.strip())
            
        except Exception as e:
            return {"error": str(e)}

# --- PHẦN TEST ---
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    load_dotenv()

    async def test_agent():
        # Tự động tìm tất cả Key có trong .env
        keys = [os.getenv(f"GROQ_API_KEY_{i}") for i in range(1, 6) if os.getenv(f"GROQ_API_KEY_{i}")]
        
        if not keys:
            print("❌ Không tìm thấy bất kỳ GROQ_API_KEY_X nào!")
            return
            
        print(f"✅ Đã tìm thấy {len(keys)} API Key. Đang dùng Key đầu tiên để test...")
        agent = RecruitAIAgent(api_key=keys[0])

        mock_jd = {"required_skills": ["Python", "AWS", "Docker"]}
        mock_resume = {"skills": ["Python", "Git"]}
        mock_raw_text = "I have deployed apps on Amazon Web Services."

        result = await agent.run_analysis(mock_jd, mock_resume, mock_raw_text)
        print("\n🎯 KẾT QUẢ TỪ AGENT (STATEGRAPH):")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    asyncio.run(test_agent())