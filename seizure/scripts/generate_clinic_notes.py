from google import genai
import os
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

def setup_client() -> genai.Client:
    """Setup and verify the Gemini client with API key"""
    # Try to get API key from environment variable
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable not found. "
            "Please set it using: export GEMINI_API_KEY='your-key-here' "
            "or add it to your environment variables."
        )

    os.environ["GEMINI_API_KEY"] = api_key
    
    return genai.Client()

def generate_clinic_note() -> Optional[str]:
    try:
        client = setup_client()
        
        # Example clinic note string here...
        example_clinic_note = """
        Epilepsy Surgery Clinic Note  
        Date: November 17, 2024  
        Patient: Mr. John Turko  
        Age: 26 years  
        Hospital Number: 12345678  
        Referring Physician: Dr. Jane Smith, Neurology  
    
        Reason for Review:  
        Post-operative follow-up after left anterior temporal lobectomy for drug-resistant epilepsy.  
    
        Diagnosis:  
        - Pre-surgical: Drug-resistant focal epilepsy with confirmed left temporal lobe seizure onset.  
        - Post-surgical: Focal epilepsy, post-resection, seizure-free since January 2023 surgery.  
    
        History:  
        Current Antiepileptic Medication:  
        Levetiracetam 500 mg twice daily, well-tolerated without side effects.  
    
        Previous Antiepileptic Medications:  
        - Lamotrigine: Discontinued in 2015 due to rash and inadequate seizure control.  
        - Carbamazepine: Discontinued in 2016 due to drowsiness and suboptimal control of seizures.  
    
        Pre-Surgical Seizure History:  
        - First Seizures (2014): Experienced two generalized tonic-clonic seizures without aura or prodrome. Witnesses noted possible preceding right leg jerking lasting a few seconds. Postictal confusion lasted approximately 20 minutes.  
        - "Absence-like" Episodes (2014–2022): Weekly episodes of staring and unresponsiveness lasting 5–10 seconds. Mr. Turko was unaware of these events and relied on observations by family and colleagues.  
        - Childhood Seizures: Febrile seizures between the ages of 2–4 years, resolved without long-term effects.  
        - Family History: No family history of epilepsy, neurological conditions, or febrile seizures. His two children are healthy without seizure activity.  
    
        Surgical History:  
        - Surgery Date: January 15, 2023.  
        - Procedure: Left anterior temporal lobectomy.  
        - Intraoperative Findings: Resected area included the left hippocampus and anterior temporal cortex, with pathology confirming hippocampal sclerosis.  
        - Post-operative Course: Uncomplicated recovery, with no neurological deficits or infections.  
    
        Post-Surgical Seizure Status:  
        - Seizure-Free Period: 22 months since surgery.  
        - Functional Outcomes: Resumed full-time work as a graphic designer and driving in February 2024 after meeting the seizure-free guidelines.  
    
        Investigations:  
        Pre-surgical Workup:  
        - MRI (2022): Demonstrated left mesial temporal sclerosis with hippocampal atrophy, no other structural abnormalities.  
        - Video EEG Monitoring (2022): Recorded five clinical seizures, all with onset in the left temporal lobe. No secondary generalization observed.  
        - Neuropsychological Assessment: Mild impairment in verbal memory consistent with left temporal dysfunction.  
        - PET Scan (2022): Hypometabolism localized to the left temporal lobe, further supporting focal epilepsy diagnosis.  
    
        Post-surgical Investigations:  
        - MRI (2023): Post-resection changes in the left anterior temporal lobe without evidence of residual or new pathology.  
        - EEG (2023): Normal background activity without epileptiform discharges.  
    
        Clinical Assessment:  
        Mr. Turko was seen in the epilepsy clinic today for his routine post-surgical follow-up. He reports no seizures, staring spells, or other episodes suggestive of epilepsy since his surgery. He has experienced no medication side effects and feels well overall. He has returned to driving, as well as to full-time work. His sleep quality and mood are good, and he denies symptoms of anxiety or depression.  
    
        Neurological examination was unremarkable, with no focal deficits. Cognitive testing in clinic revealed no changes in memory or attention since the pre-surgical neuropsychological assessment. Physical examination, including gait and coordination, was normal.  
    
        Discussion and Plan:  
        I congratulated Mr. Turko on his excellent post-surgical outcome and discussed the importance of maintaining his current treatment regimen. He was counseled on the ongoing, albeit reduced, risk of seizure recurrence even after successful surgery. The following key points were emphasized:  
        1. Long-term continuation of levetiracetam to minimize the risk of recurrence.  
        2. Lifestyle modifications, including adequate sleep, regular meals, stress management, and avoiding known triggers such as excessive alcohol.  
        3. The rare but serious risk of sudden unexpected death in epilepsy (SUDEP), which is significantly lower given his seizure freedom.  
    
        We discussed his prognosis, including the likelihood of sustained seizure freedom and potential medication tapering in the distant future if seizure freedom persists. I emphasized the need for close monitoring before any changes are made to his treatment.  
    
        Follow-up Plan:  
        - Routine follow-up in 12 months, or sooner if symptoms recur or if he has questions.  
        - Referral to neuropsychology for repeat cognitive testing in 2025 to assess long-term memory outcomes post-surgery.  
    
        Mr. Turko expressed his satisfaction with his care and stated he feels optimistic about his quality of life moving forward. He understands he can contact the clinic if needed.  
    
        Signed:  
        [Your Name, MD]  
        Consultant Epileptologist  
        [Hospital Name]  
        """

        # Create the prompt with system instructions and user request
        prompt = f"""You are an experienced epileptologist creating detailed clinical notes. Generate realistic, 
        professional clinic notes that maintain patient confidentiality while including comprehensive medical details. 
        Follow standard medical documentation practices and ensure all relevant clinical information is included.

        Using the following example clinic note as a template, generate a detailed clinic note 
        for a different patient who has undergone epilepsy surgery. Include similar sections and formatting, 
        and ensure to include information about the patient's:
        - Auras
        - Seizure frequency before surgery (days per year)
        - Seizure frequency after surgery (days per year)
        - Current seizure freedom status
        - All relevant clinical details
        
        The note should maintain the same level of detail and professional medical terminology as the example.
        All dates should be current relative to today's date of November 17, 2024.
        Make the note realistic and comparable to real clinic notes, with different patient details and medical history.

        Example Clinic Note:
        {example_clinic_note}
        """

        # Generate content using Gemini 2.5 Flash API
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        return response.text

    except ValueError as ve:
        print(f"Authentication Error: {str(ve)}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

def save_clinic_note(note: str, index: int, output_dir: str = "generated_notes"):
    """Save the generated clinic note to a file"""
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"clinic_note_{index}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(note)
    print(f"Saved clinic note {index} to {filename}")

def main():
    num_notes = 10  # Number of clinic notes to generate
    
    try:
        setup_client()
    except ValueError as e:
        print(f"Setup Error: {str(e)}")
        return

    for i in range(num_notes):
        print(f"\nGenerating clinic note {i+1}...")
        note = generate_clinic_note()
        
        if note:
            save_clinic_note(note, i+1)
            print(f"Successfully generated clinic note {i+1}")
        else:
            print(f"Failed to generate clinic note {i+1}")

if __name__ == "__main__":
    main()