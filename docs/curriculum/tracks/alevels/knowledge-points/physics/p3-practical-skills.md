---
track: alevels
subject: physics
unit: 3
unit_code: WPH13
unit_title: Practical Skills in Physics I
exam_board: Edexcel (IAL)
exam_window: 2018-spec
level: International A-level (AS)
kp_count: 8
sources:
  primary_notes: docs/curriculum/raw_pmt/Physics_Notes/Unit3_CP*.pdf  # 8 Core Practicals
  detailed_notes:
    - docs/curriculum/raw_pmt/Physics_Notes/Unit3_CP1_Free_Fall.pdf
    - docs/curriculum/raw_pmt/Physics_Notes/Unit3_CP2_Viscosity.pdf
    - docs/curriculum/raw_pmt/Physics_Notes/Unit3_CP3_Young_Modulus.pdf
    - docs/curriculum/raw_pmt/Physics_Notes/Unit3_CP4_Speed_of_Sound.pdf
    - docs/curriculum/raw_pmt/Physics_Notes/Unit3_CP5_Frequency_String.pdf
    - docs/curriculum/raw_pmt/Physics_Notes/Unit3_CP6_Diffraction_Grating.pdf
    - docs/curriculum/raw_pmt/Physics_Notes/Unit3_CP7_Resistivity.pdf
    - docs/curriculum/raw_pmt/Physics_Notes/Unit3_CP8_EMF.pdf
  past_papers: docs/curriculum/raw_pmt/Physics_papers/Unit-3/
specification_refs:
  official_spec: Edexcel IAL Physics YPH11 (Unit 3 WPH13/01) 2018 spec
  spec_section_3_1: Planning, implementing and evaluating experiments
  spec_section_3_2: Core Practicals (CP1-CP8)

# Knowledge Points — 8 Core Practicals from 2018 Edexcel IAL Physics Unit 3
knowledge_points:
  - id: kp_alevels_physics_unit3_1
    topic: CP1 — Acceleration of a Freely-Falling Object
    spec_ref: 3.2.CP1
    level: AS
    difficulty: 3/5
    weight: medium
    description: |
      Use light gates / data logger to measure the velocity of a falling
      object at two points, then derive acceleration using a = (v₂ - v₁)/t
      or via s = ut + ½at². Identify systematic errors (air resistance,
      reaction time) and random errors (timing variability). Calculate
      percentage uncertainty in g.
    method_outline:
      - Drop a card / object through two light gates separated by known distance s
      - Measure time at each gate; velocity v = length / time
      - Repeat for different heights; plot v against t or v² against s
      - Determine g from gradient (≈ 9.81 m s⁻²)
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_Notes/Unit3_CP1_Free_Fall.pdf
        type: detailed_notes

  - id: kp_alevels_physics_unit3_2
    topic: CP2 — Viscosity of a Liquid
    spec_ref: 3.2.CP2
    level: AS
    difficulty: 3/5
    weight: low
    description: |
      Measure viscosity of a liquid using Stokes' law with a ball bearing
      falling through the liquid. Time the ball between two marks at
      terminal velocity. Calculate η = 2r²g(ρ_ball - ρ_liquid) / (9v_terminal).
      Account for container wall correction.
    method_outline:
      - Drop small steel ball into measuring cylinder of liquid
      - Time ball between two marks (use ≥ 0.5 m apart for accuracy)
      - Verify terminal velocity reached (repeat at different heights)
      - Calculate η from Stokes' law
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_Notes/Unit3_CP2_Viscosity.pdf
        type: detailed_notes

  - id: kp_alevels_physics_unit3_3
    topic: CP3 — Young Modulus of a Material
    spec_ref: 3.2.CP3
    level: AS
    difficulty: 3/5
    weight: medium
    description: |
      Measure Young's modulus E = σ/ε of a wire (typically copper or
      steel) using a Searle's apparatus. Measure extension ΔL for known
      load F. Calculate stress = F/A and strain = ΔL/L. Plot stress-strain
      graph; E = gradient of linear region. Use vernier scale to reduce
      reading error.
    method_outline:
      - Set up Searle's apparatus with reference wire and test wire
      - Apply increasing loads; measure extension with vernier scale
      - Plot F vs ΔL graph; gradient = EA/L
      - Calculate E knowing A and L
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_Notes/Unit3_CP3_Young_Modulus.pdf
        type: detailed_notes

  - id: kp_alevels_physics_unit3_4
    topic: CP4 — Speed of Sound in Air
    spec_ref: 3.2.CP4
    level: AS
    difficulty: 2/5
    weight: low
    description: |
      Measure speed of sound in air using resonance in a tube (e.g.,
      Quincke tube or resonance tube method). Vary length until loud
      resonance heard; measure length L between successive resonances.
      v = 2fΔL. Alternative: two-microphone method measuring time
      difference over known distance.
    method_outline:
      - Set up resonance tube with speaker at top, water level variable
      - Lower water level until first loud resonance; record length
      - Continue to second resonance; difference = λ/2
      - v = fλ where f is known frequency of speaker
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_Notes/Unit3_CP4_Speed_of_Sound.pdf
        type: detailed_notes

  - id: kp_alevels_physics_unit3_5
    topic: CP5 — Frequency of a Vibrating String
    spec_ref: 3.2.CP5
    level: AS
    difficulty: 2/5
    weight: low
    description: |
      Use a sonometer to verify f = (1/2L)√(T/μ) for a string. Pluck
      string and adjust tension T (or length L) until string vibrates in
      resonance with known tuning fork. Record values, plot f² vs T to
      verify linear relationship.
    method_outline:
      - Place sonometer wire over bridges with adjustable length L
      - Pluck wire in resonance with tuning fork (place paper rider)
      - Record T (tension = mass on hanger × g) and L at resonance
      - Plot f² against T; gradient = 1/(4L²μ)
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_Notes/Unit3_CP5_Frequency_String.pdf
        type: detailed_notes

  - id: kp_alevels_physics_unit3_6
    topic: CP6 — Wavelength of Light Using Diffraction Grating
    spec_ref: 3.2.CP6
    level: AS
    difficulty: 3/5
    weight: medium
    description: |
      Use a diffraction grating (typically 600 lines/mm) to measure
      wavelength of laser light. Apply d sin θ = nλ. Measure angle θ for
      first and second-order maxima on both sides; average reduces
      systematic errors in grating alignment.
    method_outline:
      - Set up laser, grating, and screen at measured distance D
      - Measure distance x from central max to first-order max
      - Calculate angle: tan θ = x/D
      - λ = d sin θ / n; d = 1/(lines per metre)
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_Notes/Unit3_CP6_Diffraction_Grating.pdf
        type: detailed_notes

  - id: kp_alevels_physics_unit3_7
    topic: CP7 — Electrical Resistivity of a Material
    spec_ref: 3.2.CP7
    level: AS
    difficulty: 2/5
    weight: medium
    description: |
      Measure resistance R of a wire of known length L and cross-section
      A. Use micrometer to measure diameter. Calculate resistivity
      ρ = RA/L. Verify by repeating with different lengths and plotting
      R against L.
    method_outline:
      - Measure wire diameter with micrometer at multiple points
      - Connect wire to ammeter and voltmeter (correct configuration)
      - Measure R = V/I for various lengths
      - Plot R vs L; gradient = ρ/A
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_Notes/Unit3_CP7_Resistivity.pdf
        type: detailed_notes

  - id: kp_alevels_physics_unit3_8
    topic: CP8 — EMF and Internal Resistance
    spec_ref: 3.2.CP8
    level: AS
    difficulty: 3/5
    weight: high
    description: |
      Measure EMF ε and internal resistance r of a cell by varying
      external resistance R and measuring terminal V. Plot V against I
      (or 1/R) to find ε (y-intercept) and r (gradient magnitude).
      Apply ε = I(R + r).
    method_outline:
      - Connect cell, ammeter, voltmeter, and variable resistor
      - Record V and I for at least 6 different R values
      - Plot V on y-axis vs I on x-axis; y-intercept = ε, gradient = -r
      - Compare to V = ε - Ir
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_Notes/Unit3_CP8_EMF.pdf
        type: detailed_notes

# Unit-level metadata
paper_structure:
  total_marks: 50
  duration_minutes: 75
  question_format:
    - "All structured / free-response (no MCQ for this unit per 2018 spec)"
    - "Typically 4 questions each testing planning / implementation / evaluation skills"
    - "Each question is based on one Core Practical context (or a novel related experiment)"
  weight_to_ias: 31.25%  # 50/160 of the IAS total (160 = U1+U2+U3)
  weight_to_ial: 12.5%

qc_notes:
  - "Unit 3 has no by-topic QP/MS — only 8 Core Practical detailed notes."
  - "Past paper tests experimental technique, not just CP results; need to understand WHY each step matters."
  - "Exam-style questions: 'comment on the suitability of apparatus', 'identify sources of error', 'suggest improvements', 'plot graph and find gradient'."
  - "All CPs tested in past papers 2020-2024 (119 PDFs across Units 1-4 — Unit 3 has 29 QP+MS = 29 sessions × 2 = ~58 papers)."
  - "2018 spec changed Unit 3 to all-structured format (no MCQ) and increased marks to 50 (was 40 in old spec)."