from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from state.State import Blog_State
from dotenv import load_dotenv
from Schemas.image_schema import GlobalImagePlan
load_dotenv()
llm=ChatOpenAI(model="gpt-4.1-mini")



def merge_content(state: Blog_State):
    plan=state["plan"]
    if plan is None:
        raise ValueError("Plan is required")
    ordered_sections=[md for _, md in sorted(
        state["sections"], key=lambda x:x[0]
    )]
    body="\n\n".join(ordered_sections).strip()
    merged_md=f"# {plan.blog_title}\n\n{body}\n"
    return {"merged_md":merged_md}

DECIDE_IMAGE_SYSTEM="""You are an expert technical editor.
Decide if image/diagrams are needed for this blog.

RULES:
- Max 3 images total.
- Each image must materially improve understanding (diagram/flow/table-like visual)
- Insert placeholder exactly: [[IMAGE_1]], [[IMAGE_2]],[[IMAGE_3]]
- If no image needed: md_with_placeholders must equal input and images=[]
- avoid decorative images; Prefer technical diagram with short labels
Return strictly GlobalImagePlan
"""

def decide_images(state: Blog_State)->dict:
    planner=llm.with_structured_output(GlobalImagePlan)
    merged_md=state["merged_md"]
    plan=state["plan"]
    assert plan is not None
    image_plan=planner.invoke([
        SystemMessage(content=DECIDE_IMAGE_SYSTEM),
        HumanMessage(content=(
            f"Blog Kind: {plan.blog_kind}\n"
            f"Topic : {state['topic']}\n\n"
            "Insert placeholders + propose image prompts.\n\n"
            f"{merged_md}"

        )),
    ])
    return {
        "md_with_placeholders": image_plan.md_with_placeholders,
        "image_specs": [img.model_dump() for img in image_plan.images],
    }

