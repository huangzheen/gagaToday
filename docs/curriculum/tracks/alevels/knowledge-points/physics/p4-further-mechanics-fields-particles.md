---
track: alevels
subject: physics
unit: 4
unit_code: WPH14
unit_title: Further Mechanics, Fields and Particles
exam_board: Edexcel (IAL)
exam_window: 2018-spec
level: International A-level (A2)
kp_count: 9
sources:
  primary_notes: docs/curriculum/raw_pmt/Physics_Notes/Unit4_Combined_Notes.pdf
  detailed_notes:
    - docs/curriculum/raw_pmt/Physics_Notes/Unit4_Detailed_4.3_Further_Mechanics.pdf
    - docs/curriculum/raw_pmt/Physics_Notes/Unit4_Detailed_4.4_Electric_Magnetic_Fields.pdf
    - docs/curriculum/raw_pmt/Physics_Notes/Unit4_Detailed_4.5_Nuclear_Particle.pdf
  by_topic_qp_ms:
    set_n: docs/curriculum/raw_pmt/Physics_questions/Unit-4/
  past_papers: docs/curriculum/raw_pmt/Physics_papers/Unit-4/
specification_refs:
  official_spec: Edexcel IAL Physics YPH11 (Unit 4 WPH14/01) 2018 spec
  spec_section_4_3: Further Mechanics (momentum in 2D, circular motion)
  spec_section_4_4: Electric and Magnetic Fields (E fields, capacitance, EM induction)
  spec_section_4_5: Nuclear and Particle Physics

# Knowledge Points — 9 KP from 2018 Edexcel IAL Physics Unit 4 spec
knowledge_points:
  - id: kp_alevels_physics_unit4_1
    topic: Impulse and Momentum in 2D (Collisions)
    spec_ref: 4.3
    level: A2
    difficulty: 3/5
    weight: high
    description: |
      Extend momentum and impulse to two dimensions. Apply conservation
      of momentum separately in x and y components. Solve 2D collision
      problems (e.g., billiard-ball collision, projectile explosion).
      Use vectors throughout: p = mv, J = FΔt.
    key_formulae:
      - 2D momentum: p_x = mv_x; p_y = mv_y
      - conservation in 2D: Σp_x,before = Σp_x,after; same for y
      - impulse: FΔt = Δp (vector)
    common_mistakes:
      - Not splitting into components before applying conservation
      - Mixing momentum vectors with scalar momentum
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Impulse and Momentum QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Impulse and Momentum MS.pdf
        type: topic_ms
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Impulse and Momentum 2 QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Impulse and Momentum 2 MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit4_2
    topic: Circular Motion
    spec_ref: 4.3
    level: A2
    difficulty: 3/5
    weight: high
    description: |
      Define angular displacement, angular velocity ω = v/r. Apply
      centripetal acceleration a = v²/r = ω²r (toward centre). Identify
      centripetal force F = mv²/r as the resultant inward force (not a
      separate force). Describe conical pendulum and banked curves.
    key_formulae:
      - "ω = v/r"
      - "T = 2π/ω"
      - "a = v²/r = ω²r"  # toward centre
      - "F_centripetal = mv²/r = mω²r"
    common_mistakes:
      - Treating centripetal force as a new applied force
      - Confusing angular ω with linear v
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Circular Motion QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Circular Motion MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit4_3
    topic: Electric Fields (Point Charges and Uniform)
    spec_ref: 4.4
    level: A2
    difficulty: 3/5
    weight: medium
    description: |
      Describe electric field E as force per unit positive charge
      (E = F/Q). Field around point charge E = kQ/r² (k = 1/(4πε₀)).
      For parallel plates: E = V/d (uniform between plates). Calculate
      force on a charge F = EQ. Apply Coulomb's law F = kQ₁Q₂/r².
    key_formulae:
      - field: "E = F/Q"
      - point charge: "E = kQ/r²"
      - parallel plate: "E = V/d"
      - Coulomb: "F = kQ₁Q₂/r²"  # k = 8.99 × 10⁹ N m² C⁻²
    common_mistakes:
      - Confusing E (field) with V (potential)
      - Sign errors with charge direction
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Electric Fields QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Electric Fields MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit4_4
    topic: Capacitance (Parallel Plate)
    spec_ref: 4.4
    level: A2
    difficulty: 2/5
    weight: medium
    description: |
      Define capacitance C = Q/V. For parallel-plate capacitor
      C = ε₀A/d (A = area, d = separation). Capacitors in parallel
      add: C_total = C₁ + C₂ + ... In series: 1/C_total = 1/C₁ + 1/C₂.
      Energy stored in capacitor E = ½QV² = ½CV² = ½Q²/C.
    key_formulae:
      - "C = Q/V"
      - parallel: "C_total = C₁ + C₂"
      - series: "1/C_total = 1/C₁ + 1/C₂"
      - energy: "E = ½QV² = ½CV²"
    common_mistakes:
      - Mixing series and parallel combinations
      - Forgetting energy formula (½CV² not CV²)
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Capacitance QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Capacitance MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit4_5
    topic: Charging and Discharging Capacitors (RC Circuits)
    spec_ref: 4.4
    level: A2
    difficulty: 3/5
    weight: medium
    description: |
      Apply RC circuit equations. Time constant τ = RC. Charging:
      V(t) = V₀(1 - e^(-t/RC)). Discharging: V(t) = V₀e^(-t/RC). Identify
      half-life t_½ = RC ln 2 ≈ 0.693 RC. Interpret exponential graphs
      (log V vs t → straight line).
    key_formulae:
      - time constant: "τ = RC"
      - charging: "V(t) = V₀(1 - e^(-t/τ))"
      - discharging: "V(t) = V₀e^(-t/τ)"
      - half-life: "t_½ = τ ln 2"
    common_mistakes:
      - Mixing charging and discharging formulas
      - Forgetting to convert time to seconds
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Capacitance QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Capacitance MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit4_6
    topic: Magnetic Fields and Force on a Current-Carrying Conductor
    spec_ref: 4.4
    level: A2
    difficulty: 3/5
    weight: high
    description: |
      Describe magnetic field B around a current-carrying wire (right-hand
      grip rule) and around a bar magnet (N → S external). Force on a
      straight current-carrying wire F = BIL sin θ. Force on a moving
      charge F = BQv sin θ (Lorentz force). Describe Hall effect.
    key_formulae:
      - current-carrying wire: "F = BIL sin θ"
      - moving charge: "F = BQv sin θ"
      - magnetic flux: "Φ = BA cos θ"  # Wb
    common_mistakes:
      - Direction errors (Fleming's left-hand rule)
      - Forgetting sin θ when current/velocity not perpendicular to B
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Magnetic Fields and EM Induction QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Magnetic Fields and EM Induction MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit4_7
    topic: Electromagnetic Induction (Faraday's and Lenz's Laws)
    spec_ref: 4.4
    level: A2
    difficulty: 3/5
    weight: high
    description: |
      State Faraday's law: ε = -dΦ/dt (induced EMF = rate of change of
      flux linkage). State Lenz's law: induced current opposes change
      causing it (negative sign). Apply to rotating coil, transformer,
      eddy currents. Define transformer ratio: V_p/V_s = N_p/N_s.
    key_formulae:
      - Faraday: "ε = -N dΦ/dt"
      - transformer: "V_p/V_s = N_p/N_s"  # ideal
      - self-inductance: "ε = -L dI/dt"
    common_mistakes:
      - Forgetting the N (turns) factor
      - Sign error in Lenz's law (must be negative)
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Magnetic Fields and EM Induction QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Magnetic Fields and EM Induction MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit4_8
    topic: Charged Particles in Electric and Magnetic Fields
    spec_ref: 4.4
    level: A2
    difficulty: 3/5
    weight: medium
    description: |
      Apply Lorentz force F = BQv to determine radius of circular motion
      r = mv/(BQ) in magnetic field. Apply electric force to accelerate
      particles: eV = ½mv² (energy from p.d.). Describe velocity selector
      and mass spectrometer. Calculate e/m ratio experimentally.
    key_formulae:
      - Lorentz: "F = BQv"
      - circular path in B: "r = mv/(BQ)"
      - accelerating p.d.: "eV = ½mv²"
      - "e/m = 2V/(B²r²)"  # for mass spec
    common_mistakes:
      - Sign errors with charge in force equation
      - Confusing radius of path with radius of circular motion formula
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Charged Particles in Fields QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Charged Particles in Fields MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit4_9
    topic: Nuclear and Particle Physics (Quarks, Radioactivity, Half-Life)
    spec_ref: 4.5
    level: A2
    difficulty: 3/5
    weight: high
    description: |
      Describe nuclear structure: protons, neutrons, nucleons, isotopes.
      Identify quarks (u, d, s, c, b, t) and antiquarks. Compose hadrons
      (baryons = 3 quarks, mesons = quark + antiquark) and lepton family
      (electron, muon, tau + their neutrinos). Apply radioactive decay:
      activity A = λN, half-life t_½, decay constant λ = ln 2 / t_½.
      Apply N(t) = N₀ e^(-λt). State mass-energy equivalence E = mc².
    key_formulae:
      - decay: "N(t) = N₀ e^(-λt)"
      - activity: "A = λN"
      - half-life: "t_½ = ln 2 / λ"
      - "E = mc²"  # mass-energy
    common_mistakes:
      - Confusing decay constant λ with radioactive decay chain λ
      - Quark composition errors (proton = uud, neutron = udd)
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Nuclear and Particle Physics QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-4/Nuclear and Particle Physics MS.pdf
        type: topic_ms

# Unit-level metadata
paper_structure:
  total_marks: 90
  duration_minutes: 105  # 2018 spec: 1h 45min
  question_format:
    - "Section A: 10 multiple choice (10 marks)"
    - "Section B: short answer + structured Qs (80 marks)"
  weight_to_ial: 25%  # full A-level
  weight_to_a2: 50%  # A2 part

qc_notes:
  - "All 9 KP derived from 2018 Edexcel IAL YPH11 spec (matches 2018+ paper code WPH14/01)."
  - "2018 spec increased Unit 4 to 90 marks (from 80) and duration to 1h 45min (from 1h 35min)."
  - "Set N contains 9 unique by-topic QP/MS — each maps to one KP (or a closely-related pair)."
  - "KP4-1 covers 2D collisions, covered by both 'Impulse and Momentum' and 'Impulse and Momentum 2' QPs."
  - "Capacitance (KP4-4) and RC circuits (KP4-5) both use 'Capacitance' QP."
  - "Magnetic Fields + EM Induction (KP4-6, 4-7) both use 'Magnetic Fields and EM Induction' QP."
  - "Quark model (KP4-9) and radioactivity + half-life (KP4-9) both in 'Nuclear and Particle Physics' QP."