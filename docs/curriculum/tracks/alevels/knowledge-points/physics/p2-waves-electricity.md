---
track: alevels
subject: physics
unit: 2
unit_code: WPH12
unit_title: Waves and Electricity
exam_board: Edexcel (IAL)
exam_window: 2018-spec
level: International A-level (AS)
kp_count: 10
sources:
  primary_notes: docs/curriculum/raw_pmt/Physics_Notes/Unit2_Combined_Notes.pdf
  detailed_notes:
    - docs/curriculum/raw_pmt/Physics_Notes/Unit2_Detailed_2.3_Waves_Particle.pdf
    - docs/curriculum/raw_pmt/Physics_Notes/Unit2_Detailed_2.4_Electric_Circuits.pdf
  by_topic_qp_ms:
    set_n: docs/curriculum/raw_pmt/Physics_questions/Unit-2/
  past_papers: docs/curriculum/raw_pmt/Physics_papers/Unit-2/
specification_refs:
  official_spec: Edexcel IAL Physics YPH11 (Unit 2 WPH12/01) 2018 spec
  spec_section_2_3: Waves and Particle Nature of Light
  spec_section_2_4: Electric Circuits

# Knowledge Points — 10 KP from 2018 Edexcel IAL Physics Unit 2 spec
knowledge_points:
  - id: kp_alevels_physics_unit2_1
    topic: Progressive Waves (basics)
    spec_ref: 2.3
    level: AS
    difficulty: 2/5
    weight: high
    description: |
      Define wave as oscillation that transfers energy without net transfer
      of matter. Distinguish transverse (oscillation ⊥ propagation, e.g.
      light) from longitudinal (oscillation ∥ propagation, e.g. sound).
      Define amplitude, wavelength λ, frequency f, period T, speed
      v = fλ.
    key_formulae:
      - "v = fλ"
      - "T = 1/f"
      - phase difference Δφ = (Δx/λ) × 2π rad
    common_mistakes:
      - Confusing frequency with period
      - Mixing up longitudinal and transverse examples
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Waves QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Waves MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit2_2
    topic: Waves on Strings and Stationary Waves
    spec_ref: 2.3
    level: AS
    difficulty: 3/5
    weight: medium
    description: |
      Derive wave speed on string v = √(T/μ) where T is tension and μ
      linear density (kg/m). Describe stationary (standing) waves formed
      by superposition of two progressive waves: nodes (zero amplitude)
      and antinodes (max amplitude). Identify harmonics on a string
      fixed at both ends (λ_n = 2L/n).
    key_formulae:
      - "v = √(T/μ)"
      - harmonic n: "f_n = n/(2L) × √(T/μ)"
      - harmonics on string: "λ_n = 2L/n"
    common_mistakes:
      - Confusing string harmonics with pipe harmonics
      - Forgetting L for length in wavelength formula
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Waves on Strings QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Waves on Strings MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit2_3
    topic: Refraction, Total Internal Reflection and Polarisation
    spec_ref: 2.3
    level: AS
    difficulty: 3/5
    weight: high
    description: |
      Apply Snell's law n₁ sin θ₁ = n₂ sin θ₂. Define refractive index
      n = c/v. Critical angle sin θ_c = n₂/n₁ (when going from denser
      to less dense). Describe total internal reflection conditions.
      Explain polarisation as oscillation restricted to one plane.
    key_formulae:
      - Snell: "n₁ sin θ₁ = n₂ sin θ₂"
      - "n = c/v"
      - critical: "sin θ_c = n₂/n₁"
    common_mistakes:
      - Wrong way around in Snell's law
      - Forgetting TIR only occurs going from denser to less dense
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Refraction, Reflection and Polarisation QP 1.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Refraction, Reflection and Polarisation MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit2_4
    topic: Diffraction and Interference (Young's Double Slit)
    spec_ref: 2.3
    level: AS
    difficulty: 3/5
    weight: high
    description: |
      Describe diffraction (spreading at edges/slits) and two-source
      interference. Apply Young's double-slit equation λ = ax/D (a =
      slit separation, x = fringe spacing, D = distance to screen) for
      constructive interference. Describe path difference condition
      (nλ = constructive, (n+½)λ = destructive).
    key_formulae:
      - Young's double slit: "λ = ax/D"
      - constructive: path diff = nλ
      - destructive: path diff = (n + ½)λ
    common_mistakes:
      - Confusing slit separation a with slit width
      - Mixing up which variable is distance to screen
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Diffraction QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Diffraction MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit2_5
    topic: Charge, Current, Energy and EMF
    spec_ref: 2.4
    level: AS
    difficulty: 2/5
    weight: high
    description: |
      Define electric current I = ΔQ/Δt (ampere). Describe conduction
      in metals (drift velocity of electrons). Define EMF ε as energy
      delivered per unit charge (work done per coulomb). Define
      potential difference V = W/Q.
    key_formulae:
      - "I = Q/t"
      - "V = W/Q"
      - drift: "I = nAvq"  # n=charge carrier density, A=cross-section, v=drift velocity, q=carrier charge
    common_mistakes:
      - Confusing EMF (source) with p.d. (component)
      - Forgetting direction of conventional current (opposite to electron flow)
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Charge, Energy and Current QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Charge, Energy and Current MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit2_6
    topic: Resistance, Resistivity and Components
    spec_ref: 2.4
    level: AS
    difficulty: 2/5
    weight: high
    description: |
      Apply Ohm's law V = IR. Define resistance R = V/I (Ω). Define
      resistivity ρ = RA/L (Ω m). Calculate resistance from length and
      cross-section. Interpret I-V characteristics (linear ohmic vs
      non-linear: filament lamp, diode).
    key_formulae:
      - Ohm: "V = IR"
      - resistivity: "R = ρL/A"
      - power dissipated: "P = IV = I²R = V²/R"
    common_mistakes:
      - Confusing resistance with resistivity (one is property, other is object)
      - Forgetting R ∝ L (longer wire = more resistance)
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Resistance, Components and Resistivity QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Resistance, Components and Resistivity MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit2_7
    topic: Potential Dividers, EMF and Internal Resistance
    spec_ref: 2.4
    level: AS
    difficulty: 3/5
    weight: medium
    description: |
      Describe a potential divider: V_out = V_in × R₂/(R₁+R₂). Apply
      Kirchhoff's laws (sum of currents at a junction = 0; sum of EMFs =
      sum of p.d.s in a loop). Define internal resistance r: terminal
      V = ε - Ir. Identify short-circuit current (I = ε/r).
    key_formulae:
      - divider: "V_out = V_in × R₂/(R₁+R₂)"
      - terminal: "V = ε - Ir"
      - power dissipated in r: "P = I²r"
    common_mistakes:
      - Using divider formula for source with internal r (that's different)
      - Sign errors in Kirchhoff loop
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Potential Dividers, EMF and Internal Resistance QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Potential Dividers, EMF and Internal Resistance MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit2_8
    topic: Photons and the Photoelectric Effect
    spec_ref: 2.3
    level: AS
    difficulty: 3/5
    weight: high
    description: |
      Describe photon E = hf. Explain photoelectric effect: electrons
      emitted from metal surface when light frequency > threshold. Apply
      Einstein's photoelectric equation hf = φ + E_k(max). Threshold
      frequency f₀ corresponds to work function φ.
    key_formulae:
      - photon: "E = hf"
      - photoelectric: "hf = φ + E_k(max)"
      - work function: "φ = hf₀"
    common_mistakes:
      - Confusing intensity (rate of photons) with frequency (energy per photon)
      - Forgetting that intensity alone won't cause emission if f < f₀
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Photons QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Photons MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit2_9
    topic: Wave-Particle Duality and de Broglie
    spec_ref: 2.3
    level: AS
    difficulty: 3/5
    weight: medium
    description: |
      Describe evidence for wave-particle duality: photoelectric effect
      (light as photons) and electron diffraction (matter as waves).
      Apply de Broglie wavelength λ = h/p = h/(mv). State h = 6.63 ×
      10⁻³⁴ J s.
    key_formulae:
      - de Broglie: "λ = h/p = h/(mv)"
      - Planck constant: "h = 6.63 × 10⁻³⁴ J s"
    common_mistakes:
      - Forgetting to convert eV to J for electron KE
      - Mixing up photon E = hf with matter λ = h/p
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Photons QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Photons MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit2_10
    topic: Intensity of Radiation (Inverse Square Law)
    spec_ref: 2.3
    level: AS
    difficulty: 2/5
    weight: low
    description: |
      Define intensity I = P/A (W m⁻²). For a point source radiating
      uniformly, intensity follows inverse square law I ∝ 1/r². Apply
      to estimate power received by a detector of given area.
    key_formulae:
      - intensity: "I = P/A"
      - inverse square: "I = k/r²"  # k = P/(4π) for point source
    common_mistakes:
      - Forgetting inverse-square applies only to point sources
      - Confusing power with intensity
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Intensity of Radiation QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-2/Intensity of Radiation MS.pdf
        type: topic_ms

# Unit-level metadata
paper_structure:
  total_marks: 80
  duration_minutes: 90
  question_format:
    - "Section A: 10 multiple choice (10 marks)"
    - "Section B: short answer + structured Qs (70 marks)"
  weight_to_ias: 50%
  weight_to_ial: 25%

qc_notes:
  - "All 10 KP derived from 2018 Edexcel IAL YPH11 spec (matches 2018+ paper code WPH12/01)."
  - "Section 2.3 includes 5 wave topics (progressive waves, strings, refraction, diffraction, photons, intensity); 2.4 has 3 electric circuit topics + EMF."
  - "Set N contains 10 unique by-topic QP/MS pairs — 1:1 mapping with KP topics."
  - "Photoelectric (KP2-8) and Wave-Particle Duality (KP2-9) both use the 'Photons' QP."
  - "Internal Resistance covered in 2.7 (covered alongside potential dividers per spec)."