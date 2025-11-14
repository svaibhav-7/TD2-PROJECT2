"""
Utility script to generate prompts for the Google Form submission
"""

from prompt_utils import PromptEngineer


def main():
    """Generate recommended prompts"""
    
    print("\n" + "="*80)
    print("LLM ANALYSIS QUIZ - PROMPT GENERATION")
    print("="*80 + "\n")
    
    # Get system prompt recommendations
    print("SYSTEM PROMPT (Resists Code Word Extraction)")
    print("-" * 80)
    
    system_strategies = PromptEngineer.SYSTEM_PROMPT_STRATEGIES
    for i, (name, prompt) in enumerate(system_strategies.items(), 1):
        truncated = prompt[:100] if len(prompt) > 100 else prompt
        print(f"\n{i}. {name.upper()}")
        print(f"   Length: {len(truncated)} chars")
        print(f"   Text: {truncated}")
    
    print("\n\nRECOMMENDED SYSTEM PROMPT:")
    sys_strategy, sys_prompt = PromptEngineer.recommend_system_prompt()
    print(f"Strategy: {sys_strategy}")
    print(f"Prompt ({len(sys_prompt)} chars): {sys_prompt}")
    
    # Get user prompt recommendations
    print("\n\n" + "="*80)
    print("USER PROMPT (Extracts Code Word)")
    print("-" * 80)
    
    user_strategies = PromptEngineer.USER_PROMPT_STRATEGIES
    for i, (name, prompt) in enumerate(user_strategies.items(), 1):
        truncated = prompt[:100] if len(prompt) > 100 else prompt
        print(f"\n{i}. {name.upper()}")
        print(f"   Length: {len(truncated)} chars")
        print(f"   Text: {truncated}")
    
    print("\n\nRECOMMENDED USER PROMPT:")
    user_strategy, user_prompt = PromptEngineer.recommend_user_prompt()
    print(f"Strategy: {user_strategy}")
    print(f"Prompt ({len(user_prompt)} chars): {user_prompt}")
    
    print("\n\n" + "="*80)
    print("COPY THE RECOMMENDED PROMPTS ABOVE INTO THE GOOGLE FORM")
    print("="*80 + "\n")
    
    # Additional information
    print("\nIMPORTANT NOTES:")
    print("-" * 80)
    print("1. Both prompts must be max 100 characters")
    print("2. System prompt should PREVENT code word extraction")
    print("3. User prompt should ENABLE code word extraction")
    print("4. These will be tested against random code words and other students' prompts")
    print("5. Your score depends on effectiveness of your strategy")
    print()


if __name__ == '__main__':
    main()
