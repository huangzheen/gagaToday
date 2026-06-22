---
track: alevels
subject: physics
unit: 1
unit_code: WPH11
unit_title: Mechanics and Materials
exam_board: Edexcel (IAL)
exam_window: 2018-spec
level: International A-level (AS)
kp_count: 12
sources:
  primary_notes: docs/curriculum/raw_pmt/Physics_Notes/Unit1_Combined_Notes.pdf
  detailed_notes:
    - docs/curriculum/raw_pmt/Physics_Notes/Unit1_Detailed_*.pdf  # Combined covers both 1.3 + 1.4
  by_topic_qp_ms:
    set_n: docs/curriculum/raw_pmt/Physics_questions/Unit-1/
    set_b:  # Edexcel-IAL Set B (covers Mechanics + Experiment Qs)
    set_d:  # Edexcel-IAL Set D (Mechanics + Materials condensed)
  past_papers: docs/curriculum/raw_pmt/Physics_papers/Unit-1/
specification_refs:
  official_spec: Edexcel IAL Physics YPH11 (Unit 1 WPH11/01) 2018 spec
  spec_section_1_3: Mechanics (kinematics, dynamics, work/energy, momentum)
  spec_section_1_4: Materials (density, upthrust, fluids, stress-strain, Young's modulus)

# Knowledge Points — 12 KP from 2018 Edexcel IAL Physics Unit 1 spec
knowledge_points:
  - id: kp_alevels_physics_unit1_1
    topic: Vectors and Scalars
    spec_ref: 1.3
    level: AS
    difficulty: 2/5
    weight: low
    description: |
      Distinguish vector quantities (displacement, velocity, acceleration,
      force, momentum) from scalar quantities (mass, time, speed, distance,
      energy). Resolve a vector into perpendicular components, add vectors
      graphically (head-to-tail) and by calculation (components or cosine
      rule).
    key_formulae:
      - R² = A² + B² + 2AB cos(θ)  # cosine rule for two vectors
      - R_x = A_x + B_x; R_y = A_y + B_y  # component addition
    common_mistakes:
      - Confusing speed with velocity (vector vs scalar)
      - Forgetting direction in vector answer
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Vectors QP.pdf
        type: topic_qp
        source: Edexcel IAL Set N
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Vectors MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit1_2
    topic: Kinematics (suvat equations)
    spec_ref: 1.3
    level: AS
    difficulty: 2/5
    weight: high
    description: |
      Use equations of uniformly accelerated motion: v = u + at, s = ut + ½at²,
      s = ½(u+v)t, v² = u² + 2as. Interpret displacement-time and
      velocity-time graphs (gradient = velocity or acceleration; area =
      displacement). Understand acceleration as rate of change of velocity.
    key_formulae:
      - "v = u + at"
      - "s = ut + ½at²"
      - "s = ½(u+v)t"
      - "v² = u² + 2as"
    common_mistakes:
      - Sign error: deceleration must give negative a
      - Misreading graph gradient (s-t) as acceleration
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Kinematics QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Kinematics MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit1_3
    topic: Projectile Motion (2D under gravity)
    spec_ref: 1.3
    level: AS
    difficulty: 3/5
    weight: medium
    description: |
      Resolve projectile motion into independent horizontal (constant
      velocity) and vertical (uniform acceleration g=9.81 m/s²) components.
      Apply suvat in each direction. Calculate range, max height, time of
      flight.
    key_formulae:
      - horizontal: v_x = constant = u cos(θ)
      - vertical: a_y = -g; v_y = u sin(θ) - gt
      - time of flight: T = 2u sin(θ)/g
      - range: R = u² sin(2θ)/g
    common_mistakes:
      - Treating horizontal and vertical components as coupled
      - Forgetting to split into components at start
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Kinematics QP.pdf
        type: topic_qp  # projectile questions embedded
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Kinematics MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit1_4
    topic: Dynamics (Newton's three laws)
    spec_ref: 1.3
    level: AS
    difficulty: 3/5
    weight: high
    description: |
      Apply Newton's three laws: (1) inertia, (2) F=ma with F the resultant
      unbalanced force, (3) equal and opposite reactions. Draw free-body
      diagrams. Use weight W = mg near Earth's surface. Identify tension,
      normal force, friction.
    key_formulae:
      - "F = ma"
      - "W = mg"  # g ≈ 9.81 m s⁻²
      - friction F ≤ μR
    common_mistakes:
      - Confusing mass (kg) with weight (N)
      - Forgetting to subtract reaction from weight for net force
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Forces and Moments QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Forces and Moments MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit1_5
    topic: Moments, Couples and Torque
    spec_ref: 1.3
    level: AS
    difficulty: 3/5
    weight: medium
    description: |
      Define moment M = Fd (force × perpendicular distance from pivot).
      Apply the principle of moments for equilibrium: sum of clockwise
      moments = sum of anticlockwise moments about a point. Identify a
      couple (two equal, opposite, parallel forces producing rotation).
    key_formulae:
      - "M = Fd"  # moment in N m
      - equilibrium: Σ M_cw = Σ M_acw
    common_mistakes:
      - Using total distance instead of perpendicular distance
      - Missing a force in moment sum (e.g., reaction at pivot)
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Forces and Moments QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Forces and Moments MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit1_6
    topic: Work, Energy and Power
    spec_ref: 1.3
    level: AS
    difficulty: 3/5
    weight: high
    description: |
      Define work W = Fs cos(θ) and energy (kinetic ½mv², gravitational
      mgh, elastic ½kx²). Apply conservation of energy. Define power
      P = W/t = Fv (rate of doing work). Distinguish efficiency =
      useful output / total input.
    key_formulae:
      - "W = Fs cos(θ)"
      - "E_k = ½mv²"
      - "E_p = mgh"
      - "E_e = ½kx²"  # elastic (spring)
      - "P = W/t = Fv"
      - "η = useful power out / total power in"
    common_mistakes:
      - Mixing up kinetic and gravitational energy signs
      - Forgetting to include all energy transfers
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Work, Energy and Power QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Work, Energy and Power MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit1_7
    topic: Momentum and Impulse (1D)
    spec_ref: 1.3
    level: AS
    difficulty: 3/5
    weight: high
    description: |
      Define linear momentum p = mv. State conservation of linear momentum
      for an isolated system. Define impulse J = FΔt = Δp (N s). Apply
      to 1D elastic and inelastic collisions, including explosions.
    key_formulae:
      - "p = mv"  # kg m s⁻¹
      - impulse: "FΔt = Δp"
      - conservation: Σp_before = Σp_after
    common_mistakes:
      - Forgetting vector direction in 1D collisions
      - Confusing elastic (KE conserved) with inelastic (KE lost)
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Momentum QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Momentum MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit1_8
    topic: Density, Upthrust and Archimedes Principle
    spec_ref: 1.4
    level: AS
    difficulty: 2/5
    weight: medium
    description: |
      Define density ρ = m/V. Apply Archimedes principle: upthrust = weight
      of displaced fluid. Determine whether object floats (ρ_object <
      ρ_fluid), sinks, or is in equilibrium.
    key_formulae:
      - "ρ = m/V"  # kg m⁻³
      - upthrust U = ρ_fluid × V_displaced × g
      - floating: weight = upthrust
    common_mistakes:
      - Mixing up densities of object vs fluid
      - Forgetting g in upthrust
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Density and Upthrust QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Density and Upthrust MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit1_9
    topic: Fluid Pressure and Flow
    spec_ref: 1.4
    level: AS
    difficulty: 3/5
    weight: medium
    description: |
      Calculate pressure P = F/A and fluid pressure P = ρgh (hydrostatic).
      Apply principle of hydraulic systems (Pascal). Describe laminar vs
      turbulent flow. Apply continuity equation A₁v₁ = A₂v₂. State
      Bernoulli effect qualitatively (faster flow → lower pressure).
    key_formulae:
      - "P = F/A"  # Pa
      - "P = ρgh"  # hydrostatic
      - continuity: "A₁v₁ = A₂v₂"
    common_mistakes:
      - Forgetting hydrostatic pressure increases with depth
      - Confusing laminar and turbulent flow conditions
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Fluids QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Fluids MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit1_10
    topic: Hooke's Law and Elastic Deformation
    spec_ref: 1.4
    level: AS
    difficulty: 2/5
    weight: high
    description: |
      Apply Hooke's law F = kx (within elastic limit). Interpret
      force-extension graphs (linear region gradient = spring constant k).
      Distinguish elastic deformation (recoverable) from plastic
      (permanent).
    key_formulae:
      - "F = kx"  # k in N m⁻¹
      - elastic energy: "E_e = ½kx²"
      - elastic limit = max F for linear F-x behaviour
    common_mistakes:
      - Applying F=kx beyond elastic limit
      - Confusing spring constant k with stiffness
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Hooke's Law and Young's Modulus QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Hooke's Law and Young's Modulus MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit1_11
    topic: Stress, Strain and Young's Modulus
    spec_ref: 1.4
    level: AS
    difficulty: 3/5
    weight: high
    description: |
      Define tensile stress σ = F/A, tensile strain ε = ΔL/L. Apply
      Young's modulus E = σ/ε (Pa). Interpret stress-strain graphs:
      linear region → elastic; yield point → plastic region; ultimate
      tensile stress and breaking stress.
    key_formulae:
      - "σ = F/A"  # Pa
      - "ε = ΔL/L"  # dimensionless
      - "E = σ/ε"
      - elastic energy per unit volume: "u = ½ × stress × strain"
    common_mistakes:
      - Forgetting A in denominator of stress
      - Confusing Young's modulus with spring constant
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Hooke's Law and Young's Modulus QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Hooke's Law and Young's Modulus MS.pdf
        type: topic_ms

  - id: kp_alevels_physics_unit1_12
    topic: Drag, Terminal Velocity and Stokes' Law
    spec_ref: 1.4
    level: AS
    difficulty: 3/5
    weight: low
    description: |
      Describe drag force F_d ∝ v (laminar, Stokes) and F_d ∝ v² (turbulent).
      At terminal velocity, weight = drag (no acceleration). Describe
      viscosity η and apply Stokes' law F = 6πηrv for small spheres in
      laminar flow.
    key_formulae:
      - Stokes (laminar): "F = 6πηrv"
      - turbulent: "F_d ∝ v²"
      - terminal velocity: "W = F_d"
    common_mistakes:
      - Mixing up Stokes (laminar) and drag (turbulent) regimes
      - Forgetting radius in Stokes' law
    by_topic_refs:
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Fluids QP.pdf
        type: topic_qp
      - file: docs/curriculum/raw_pmt/Physics_questions/Unit-1/Fluids MS.pdf
        type: topic_ms

# Unit-level metadata
paper_structure:
  total_marks: 80
  duration_minutes: 90
  question_format:
    - "Section A: 10 multiple choice (10 marks)"
    - "Section B: short answer + structured Qs across topics (70 marks)"
  weight_to_ias: 50%  # counts as 50% of International AS
  weight_to_ial: 25%  # counts as 25% of full IAL (with M1 5-6)

qc_notes:
  - "All 12 KP derived from 2018 Edexcel IAL YPH11 spec (matches 2018+ paper code WPH11/01)."
  - "By-topic QP/MS sourced from PMT Set N (Edexcel IAL flagged)."
  - "PMT Combined Notes is a factsheet collection — used as supplementary reference, content paraphrased in KP descriptions."
  - "Past papers 2020-2024 + Specimen downloaded (119 PDFs across Units 1-4)."
  - "Vectors and Projectiles both appear in Set N 'Kinematics' — single QP covers multiple topics."
  - "Terminal Velocity covered as 'viscous drag' subset in Set N 'Fluids' QP."