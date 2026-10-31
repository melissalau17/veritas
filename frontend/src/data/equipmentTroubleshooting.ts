import type { InvestigationResult, SegmentationResult } from "@/lib/api";

export interface ComponentConfig {
  name: string;
  category: string;
  relevance: "high" | "moderate" | "secondary";
  box: { left: number; top: number; right: number; bottom: number };
  description: string;
  records: Array<{ source: string; type: string; summary: string }>;
}

export interface EquipmentTroubleshootingConfig {
  tag: string;
  name: string;
  equipmentType: string;
  area: string;
  investigationId: string;
  problemStatement: string;
  recentMaintenance: { wo: string; date: string; summary: string };
  historicalAnalogue: { doc: string; summary: string };
  standard: string;
  approvedOffset: string;
  imageUrl: string;
  components: ComponentConfig[];
  initialResult: InvestigationResult;
}

export const equipmentTroubleshootingConfigs: Record<string, EquipmentTroubleshootingConfig> = {
  "P-101": {
    tag: "P-101",
    name: "Centrifugal Pump",
    equipmentType: "Centrifugal Pump (CP-200)",
    area: "Process Area A",
    investigationId: "inv_p101_init",
    problemStatement:
      "Pump P-101 has abnormal vibration after its coupling was replaced. What should the engineer investigate?",
    recentMaintenance: {
      wo: "WO-1842",
      date: "2026-10-27",
      summary: "Flexible coupling replaced due to wear; alignment check noted per MNT-014",
    },
    historicalAnalogue: {
      doc: "RCA-017",
      summary: "Coupling misalignment after coupling maintenance; realigned per MNT-014 Rev 2",
    },
    standard: "MNT-014 Rev 4",
    approvedOffset: "0.08 mm",
    imageUrl: "/pump_p101_assembly.jpg",
    components: [
      {
        name: "flexible coupling",
        category: "power transmission",
        relevance: "high",
        box: { left: 387, top: 179, right: 522, bottom: 380 },
        description:
          "Mechanical transmission interface connecting motor and pump shafts. Primary focal component for post-coupling-replacement vibration.",
        records: [
          {
            source: "WO-1842.txt",
            type: "Work Order",
            summary: "Flexible coupling replaced due to wear (2026-10-27).",
          },
          {
            source: "RCA-017.txt",
            type: "Historical RCA",
            summary: "High vibration detected after coupling maintenance; root cause: coupling misalignment.",
          },
          {
            source: "MNT-014-Rev4.txt",
            type: "Approved Standard",
            summary: "Pump Coupling Alignment Procedure (maximum allowable offset: 0.08 mm).",
          },
        ],
      },
      {
        name: "electric motor",
        category: "driver",
        relevance: "secondary",
        box: { left: 72, top: 156, right: 387, bottom: 403 },
        description:
          "Primary 3-phase AC induction driver motor (45 kW, 2950 RPM) delivering rotational drive torque to the pump via flexible coupling.",
        records: [
          {
            source: "RCA-017.txt",
            type: "Root Cause Analysis",
            summary: "Corrective Action: Realign pump and motor shafts according to approved procedure.",
          },
          {
            source: "OEM-Pump-Manual.txt",
            type: "Technical Manual",
            summary: "Step 4: Verify driver motor mounting bolts, baseplate level, and alignment.",
          },
        ],
      },
      {
        name: "centrifugal pump",
        category: "pump",
        relevance: "high",
        box: { left: 522, top: 140, right: 828, bottom: 420 },
        description:
          "CP-200 centrifugal pump casing, impeller, and suction/discharge nozzles generating process flow.",
        records: [
          {
            source: "OEM-Pump-Manual.txt",
            type: "Technical Manual",
            summary: "CP-200 Centrifugal Pump operational procedures and baseline vibration envelopes.",
          },
          {
            source: "equipment_register.json",
            type: "Asset Register",
            summary: "Asset P-101: Centrifugal Pump Model CP-200, Process Area A.",
          },
        ],
      },
      {
        name: "bearing housing",
        category: "bearing assembly",
        relevance: "moderate",
        box: { left: 504, top: 201, right: 630, bottom: 358 },
        description:
          "Pump drive-end and non-drive-end bearing assembly supporting radial and thrust loads.",
        records: [
          {
            source: "OEM-Pump-Manual.txt",
            type: "Technical Manual",
            summary: "Step 3: Check bearing condition, lubrication quality, and operating temperature.",
          },
          {
            source: "RCA-022.txt",
            type: "Analogous RCA",
            summary: "High vibration caused by bearing degradation due to lubricant contamination (CP-100 series).",
          },
        ],
      },
    ],
    initialResult: {
      incident: {
        asset_id: "P-101",
        equipment_type: "Centrifugal Pump",
        symptom: "abnormal vibration",
        context: "after its coupling was replaced",
      },
      observations: [
        {
          id: "WO-1842",
          source: "WO-1842.txt",
          document_type: "work_order",
          content: "Flexible coupling replaced due to wear. Alignment was checked according to MNT-014.",
          relevance: "18",
        },
      ],
      evidence: [
        {
          id: "WO-1842",
          source: "WO-1842.txt",
          document_type: "work_order",
          content: "Flexible coupling replaced due to wear. Alignment was checked according to MNT-014.",
          relevance: "18",
        },
        {
          id: "RCA-017",
          source: "RCA-017.txt",
          document_type: "root_cause_analysis",
          content:
            "High vibration detected after coupling maintenance. Root cause: Coupling misalignment. Realign according to MNT-014 Revision 2.",
          relevance: "21",
        },
        {
          id: "MNT-014-Rev4",
          source: "MNT-014-Rev4.txt",
          document_type: "procedure",
          content: "Status: CURRENT. Maximum allowable offset: 0.08 mm. Revision 4 supersedes Revision 2.",
          relevance: "6",
          status: "CURRENT",
          revision: 4,
        },
        {
          id: "MNT-014-Rev2",
          source: "MNT-014-Rev2.txt",
          document_type: "procedure",
          content: "Status: SUPERSEDED. Maximum allowable offset: 0.15 mm.",
          relevance: "6",
          status: "SUPERSEDED",
          revision: 2,
        },
        {
          id: "OEM-Pump-Manual",
          source: "OEM-Pump-Manual.txt",
          document_type: "manual",
          content:
            "CP-200 Centrifugal Pump. For abnormal vibration following coupling maintenance: verify coupling alignment, inspect coupling condition, check bearing condition.",
          relevance: "10",
        },
      ],
      relevant_evidence: [],
      revision_checks: [
        {
          document_id: "MNT-014",
          referenced_revision: 2,
          current_revision: 4,
          referenced_source: "MNT-014-Rev2.txt",
          current_source: "MNT-014-Rev4.txt",
          status: "superseded",
        },
      ],
      conflicts: [
        {
          type: "revision_conflict",
          title: "Historical procedure MNT-014 is superseded",
          description:
            "RCA-017.txt references MNT-014 Rev 2, while Rev 4 is current. Historical tolerance: 0.15 mm, Current tolerance: 0.08 mm.",
          sources: ["RCA-017.txt", "MNT-014-Rev2.txt", "MNT-014-Rev4.txt"],
          severity: "warning",
        },
      ],
      hypotheses: [
        {
          id: "H1",
          title: "Coupling misalignment",
          status: "strong",
          supporting_evidence: ["RCA-017.txt", "WO-1842.txt", "OEM-Pump-Manual.txt"],
          contradicting_evidence: [],
          missing_evidence: ["Current alignment measurement", "Current vibration spectrum data"],
          confirmed: false,
        },
      ],
      missing_information: [
        "Current coupling alignment measurement",
        "Current vibration spectrum data",
        "Post-maintenance vibration baseline",
        "Alignment method and tools used during recent coupling replacement",
      ],
      investigation_steps: [
        "Measure current coupling alignment using MNT-014 Rev 4 procedure (tolerance: 0.08 mm)",
        "Collect vibration spectrum data and compare to baseline",
        "Verify alignment method used during WO-1842 coupling replacement",
        "Inspect coupling condition and installation",
        "Check bearing condition per OEM manual recommendations",
        "Compare current readings against OEM CP-200 specifications",
      ],
      claims: [
        {
          id: "CLM-001",
          text: "Coupling misalignment is a relevant investigation path based on historical evidence.",
          type: "investigation_hypothesis",
          supporting_sources: ["RCA-017.txt", "WO-1842.txt"],
          applicability_status: "same asset and component",
          revision_warning:
            "RCA-017 references superseded MNT-014 Rev 2; current Rev 4 has tighter tolerance (0.08 mm vs 0.15 mm)",
          status: "supported",
        },
        {
          id: "CLM-002",
          text: "Current alignment procedure MNT-014 Rev 4 specifies maximum offset of 0.08 mm.",
          type: "procedural_requirement",
          supporting_sources: ["MNT-014-Rev4.txt"],
          applicability_status: "current approved procedure",
          revision_warning: null,
          status: "supported",
        },
        {
          id: "CLM-003",
          text: "Coupling misalignment is NOT confirmed. Current alignment has not been measured.",
          type: "uncertainty_statement",
          supporting_sources: [],
          applicability_status: "pending field measurement",
          revision_warning: null,
          status: "unsupported",
        },
      ],
      trace: [
        { type: "incident_parsed", message: "Asset P-101 identified — abnormal vibration" },
        { type: "evidence_search", message: "Retrieved 5 relevant documents" },
        { type: "historical_match", message: "Found related incident: RCA-017.txt" },
        { type: "reference_check", message: "RCA-017.txt references MNT-014 Rev 2" },
        { type: "revision_warning", message: "Rev 2 superseded by Rev 4" },
        {
          type: "conflict_detected",
          message: "Maximum allowable offset changed from 0.15 mm to 0.08 mm",
        },
      ],
      ai_synthesis_status: "active",
    },
  },

  "EA-5601": {
    tag: "EA-5601",
    name: "Solvent Heater",
    equipmentType: "Shell & Tube Heat Exchanger",
    area: "Polymerization Section",
    investigationId: "inv_ea5601_init",
    problemStatement:
      "Solvent Heater EA-5601 has high tube differential pressure and low solvent outlet temperature after recent maintenance.",
    recentMaintenance: {
      wo: "WO-240110",
      date: "2024-12-13",
      summary: "Tube restriction confirmed from hexane and polymer-fines deposits in tube bores",
    },
    historicalAnalogue: {
      doc: "WO-240115",
      summary: "PDT-5605 impulse lines plugged with fines; cleaned lines and re-zeroed transmitter before cleaning bundle",
    },
    standard: "ENG-STD-HEX-014 Rev 3",
    approvedOffset: "0.45 bar dP",
    imageUrl: "/equipment/ea5601_heat_exchanger.svg",
    components: [
      {
        name: "tube bundle",
        category: "heat transfer core",
        relevance: "high",
        box: { left: 240, top: 160, right: 660, bottom: 390 },
        description:
          "246-tube bundle (AISI 316L) subject to hexane process flow and polymer-fines deposition.",
        records: [
          {
            source: "WO-240110",
            type: "Work Order",
            summary: "High tube dP and low outlet temperature traced to hexane and polymer fines in tube bores.",
          },
          {
            source: "WO-240119",
            type: "Work Order",
            summary: "Bundle inspection found general fouling; 246 tubes UT-tested, hydro-blasted, reinstalled.",
          },
        ],
      },
      {
        name: "channel head",
        category: "distribution chamber",
        relevance: "moderate",
        box: { left: 70, top: 150, right: 240, bottom: 400 },
        description:
          "Inlet/outlet solvent channel head with partition pass plates and process nozzle connections.",
        records: [
          {
            source: "WO-240111",
            type: "Work Order",
            summary: "Channel flange hexane weep repaired with fresh spiral-wound 316L/graphite gasket.",
          },
        ],
      },
      {
        name: "impulse sensing lines",
        category: "instrumentation",
        relevance: "high",
        box: { left: 450, top: 90, right: 620, bottom: 180 },
        description:
          "PDT-5605 differential pressure impulse sensing tubes measuring bundle head-loss.",
        records: [
          {
            source: "WO-240115",
            type: "Failure Memory",
            summary: "PDT-5605 lines plugged with fines; must be flushed before diagnosing internal bundle fouling.",
          },
        ],
      },
      {
        name: "shell & baffle assembly",
        category: "shell side",
        relevance: "secondary",
        box: { left: 240, top: 380, right: 660, bottom: 480 },
        description:
          "Carbon steel shell body housing low-pressure steam utility medium and segment baffles.",
        records: [
          {
            source: "ENG-STD-HEX-014",
            type: "Engineering Standard",
            summary: "Maximum allowable shell-side steam pressure 3.5 barg; condensation drainage criteria.",
          },
        ],
      },
    ],
    initialResult: {
      incident: {
        asset_id: "EA-5601",
        equipment_type: "Shell & Tube Heat Exchanger",
        symptom: "high tube differential pressure and low solvent outlet temperature",
        context: "after recent maintenance and bundle turnaround",
      },
      observations: [
        {
          id: "WO-240110",
          source: "WO-240110",
          document_type: "work_order",
          content: "High tube dP and low outlet temperature traced to hexane and polymer-fines deposits in tube bores.",
          relevance: "24",
        },
      ],
      evidence: [
        {
          id: "WO-240110",
          source: "WO-240110",
          document_type: "work_order",
          content: "Confirmed process restriction: tube bores plugged with polymer fines; dP reached 1.1 bar.",
          relevance: "24",
        },
        {
          id: "WO-240115",
          source: "WO-240115",
          document_type: "work_order",
          content: "Check sensing path: PDT-5605 impulse lines plugged with fines; cleared and transmitter re-zeroed.",
          relevance: "20",
        },
        {
          id: "WO-240119",
          source: "WO-240119",
          document_type: "work_order",
          content: "Known bundle fouling: 246 tubes UT-tested, cleaned and re-installed per maintenance cycle.",
          relevance: "18",
        },
        {
          id: "ENG-STD-HEX-014-Rev3",
          source: "ENG-STD-HEX-014-Rev3",
          document_type: "procedure",
          content: "Status: CURRENT. Maximum allowable tube dP: 0.45 bar before mandatory offline bundle cleaning.",
          relevance: "15",
          status: "CURRENT",
          revision: 3,
        },
      ],
      relevant_evidence: [],
      revision_checks: [
        {
          document_id: "ENG-STD-HEX-014",
          referenced_revision: 1,
          current_revision: 3,
          referenced_source: "ENG-STD-HEX-014-Rev1",
          current_source: "ENG-STD-HEX-014-Rev3",
          status: "superseded",
        },
      ],
      conflicts: [
        {
          type: "operational_conflict",
          title: "Sensing Path vs Real Bundle Fouling Conflict",
          description:
            "WO-240115 warns that plugged PDT-5605 impulse lines mimic tube bundle fouling. Sensing verification must precede bundle pulling.",
          sources: ["WO-240115", "WO-240110", "ENG-STD-HEX-014-Rev3"],
          severity: "warning",
        },
      ],
      hypotheses: [
        {
          id: "H1",
          title: "PDT-5605 impulse-line plugging (False fouling indication)",
          status: "strong",
          supporting_evidence: ["WO-240115"],
          contradicting_evidence: [],
          missing_evidence: ["Field blowdown of impulse lines", "Transmitter zero verification against digital manometer"],
          confirmed: false,
        },
        {
          id: "H2",
          title: "Internal tube-bore fouling by polymer fines",
          status: "moderate",
          supporting_evidence: ["WO-240110", "WO-240119"],
          contradicting_evidence: [],
          missing_evidence: ["Simultaneous solvent outlet temperature drop confirmation", "Flow rate vs dP correlation"],
          confirmed: false,
        },
      ],
      missing_information: [
        "Transmitter PDT-5605 manifold zero differential check reading",
        "Solvent mass flow rate during abnormal dP observation",
        "Shell-side steam pressure and condensate pot subcooling temperature",
      ],
      investigation_steps: [
        "1. Perform three-valve manifold zero test on transmitter PDT-5605 per ENG-STD-HEX-014 Rev 3",
        "2. Flush high-pressure and low-pressure impulse lines to clear potential polymer fines",
        "3. Cross-check thermal duty: verify if low outlet temperature correlates with reduced solvent flow",
        "4. If dP remains above 0.45 bar after sensing check, schedule offline chemical bundle wash",
      ],
      claims: [
        {
          id: "CLM-001",
          text: "Impulse line plugging must be ruled out before authorizing expensive heat exchanger bundle removal.",
          type: "investigation_hypothesis",
          supporting_sources: ["WO-240115"],
          applicability_status: "exact asset and transmitter match",
          revision_warning: null,
          status: "supported",
        },
        {
          id: "CLM-002",
          text: "Current allowable differential pressure across EA-5601 tube bundle is 0.45 bar under Rev 3 standard.",
          type: "procedural_requirement",
          supporting_sources: ["ENG-STD-HEX-014-Rev3"],
          applicability_status: "current approved procedure",
          revision_warning: "Historical Rev 1 permitted 0.70 bar; current limit is 0.45 bar",
          status: "supported",
        },
        {
          id: "CLM-003",
          text: "Tube bundle fouling is NOT confirmed until transmitter zero has been physically validated in the field.",
          type: "uncertainty_statement",
          supporting_sources: [],
          applicability_status: "pending field verification",
          revision_warning: null,
          status: "unsupported",
        },
      ],
      trace: [
        { type: "incident_parsed", message: "Asset EA-5601 identified — high tube dP and low outlet temp" },
        { type: "evidence_search", message: "Retrieved 4 maintenance records from LLDPE dataset" },
        { type: "historical_match", message: "Found repeated pattern in WO-240115 & WO-240110" },
        { type: "conflict_detected", message: "Sensing line plugging mimics bundle fouling" },
        { type: "revision_warning", message: "ENG-STD-HEX-014 Rev 1 superseded by Rev 3" },
      ],
      ai_synthesis_status: "active",
    },
  },

  "GA-1201A": {
    tag: "GA-1201A",
    name: "Hexane Feed Pump",
    equipmentType: "Centrifugal Process Pump (API 610)",
    area: "Hexane Storage & Feed",
    investigationId: "inv_ga1201a_init",
    problemStatement:
      "Hexane Feed Pump GA-1201A has elevated seal chamber temperature and seal weeping after cartridge replacement.",
    recentMaintenance: {
      wo: "WO-240092",
      date: "2024-11-18",
      summary: "Dual mechanical seal cartridge replaced; barrier fluid reservoir refilled",
    },
    historicalAnalogue: {
      doc: "RCA-GA1201-04",
      summary: "Barrier fluid circulation loss caused dry-running of inner seal faces",
    },
    standard: "API-STD-682 / MNT-022 Rev 3",
    approvedOffset: "1.5 bar delta P",
    imageUrl: "/equipment/ga1201a_feed_pump.svg",
    components: [
      {
        name: "mechanical seal",
        category: "containment",
        relevance: "high",
        box: { left: 410, top: 190, right: 510, bottom: 340 },
        description: "API 682 Dual pressurized cartridge seal with Plan 53A barrier fluid loop.",
        records: [
          {
            source: "WO-240092",
            type: "Work Order",
            summary: "Dual mechanical seal cartridge replaced and tested.",
          },
        ],
      },
      {
        name: "centrifugal pump",
        category: "pump casing",
        relevance: "high",
        box: { left: 522, top: 140, right: 828, bottom: 420 },
        description: "API 610 OH2 overhung centrifugal pump casing delivering clean hexane.",
        records: [
          {
            source: "API-STD-682",
            type: "Standard",
            summary: "Barrier fluid delta P must maintain minimum 1.5 bar over stuffing box pressure.",
          },
        ],
      },
      {
        name: "electric motor",
        category: "driver",
        relevance: "secondary",
        box: { left: 72, top: 156, right: 387, bottom: 403 },
        description: "Explosion-proof 30 kW motor driving hexane pump via flexible coupling.",
        records: [
          {
            source: "WO-240088",
            type: "Work Order",
            summary: "Motor insulation resistance and vibration checks within normal parameters.",
          },
        ],
      },
    ],
    initialResult: {
      incident: {
        asset_id: "GA-1201A",
        equipment_type: "Centrifugal Pump",
        symptom: "elevated seal chamber temperature and minor product weeping",
        context: "after mechanical seal cartridge replacement",
      },
      observations: [
        {
          id: "WO-240092",
          source: "WO-240092",
          document_type: "work_order",
          content: "Dual cartridge seal installed. Post-startup note: barrier fluid level fluctuating.",
          relevance: "22",
        },
      ],
      evidence: [
        {
          id: "WO-240092",
          source: "WO-240092",
          document_type: "work_order",
          content: "Mechanical seal cartridge replaced per MNT-022. Barrier reservoir pressurized to 4.0 barg.",
          relevance: "22",
        },
        {
          id: "RCA-GA1201-04",
          source: "RCA-GA1201-04",
          document_type: "root_cause_analysis",
          content: "Inner face overheating occurred when pumping ring recirculation was air-locked.",
          relevance: "19",
        },
        {
          id: "MNT-022-Rev3",
          source: "MNT-022-Rev3",
          document_type: "procedure",
          content: "Status: CURRENT. Pumping ring vent must be bled before energizing motor.",
          relevance: "14",
          status: "CURRENT",
          revision: 3,
        },
      ],
      relevant_evidence: [],
      revision_checks: [
        {
          document_id: "MNT-022",
          referenced_revision: 1,
          current_revision: 3,
          referenced_source: "MNT-022-Rev1",
          current_source: "MNT-022-Rev3",
          status: "superseded",
        },
      ],
      conflicts: [
        {
          type: "procedure_conflict",
          title: "Venting step omitted in historical procedure",
          description:
            "Older Rev 1 procedure omitted the compulsory seal gland vent bleed, risking vapor lock in barrier circulation.",
          sources: ["MNT-022-Rev1", "MNT-022-Rev3"],
          severity: "warning",
        },
      ],
      hypotheses: [
        {
          id: "H1",
          title: "Barrier fluid loop vapor lock / unvented seal chamber",
          status: "strong",
          supporting_evidence: ["WO-240092", "RCA-GA1201-04"],
          contradicting_evidence: [],
          missing_evidence: ["High-point vent bleeding verification", "Barrier reservoir thermowell reading"],
          confirmed: false,
        },
      ],
      missing_information: [
        "Plan 53A barrier fluid reservoir pressure and temperature",
        "Suction and discharge process pressure readings",
      ],
      investigation_steps: [
        "1. Check Plan 53A seal pot pressure and confirm minimum 1.5 bar differential over stuffing box",
        "2. Bleed high-point vent on mechanical seal gland to eliminate trapped vapor",
        "3. Check barrier circulation cooling loop tubing for thermal gradient",
      ],
      claims: [
        {
          id: "CLM-001",
          text: "Seal chamber vapor lock is the leading candidate based on post-replacement failure memory.",
          type: "investigation_hypothesis",
          supporting_sources: ["RCA-GA1201-04", "WO-240092"],
          applicability_status: "exact asset and model match",
          revision_warning: null,
          status: "supported",
        },
      ],
      trace: [
        { type: "incident_parsed", message: "Asset GA-1201A identified — seal chamber temp & weeping" },
        { type: "evidence_search", message: "Retrieved 3 seal maintenance procedures" },
        { type: "historical_match", message: "Matched RCA-GA1201-04 barrier circulation failure" },
      ],
      ai_synthesis_status: "active",
    },
  },

  "CT-7801": {
    tag: "CT-7801",
    name: "Cooling Tower Cell Fan",
    equipmentType: "Induced Draft Cooling Tower Fan",
    area: "Cooling Water System",
    investigationId: "inv_ct7801_init",
    problemStatement:
      "Cooling Tower Cell Fan CT-7801 has high vibration on composite drive-shaft after coupling replacement.",
    recentMaintenance: {
      wo: "WO-240169",
      date: "2024-10-28",
      summary: "Composite floating-shaft coupling replaced due to wear; dynamic balancing pending",
    },
    historicalAnalogue: {
      doc: "WO-240163",
      summary: "VSHH-7802 vibration alarm caused by leading-edge erosion on FRP fan blade",
    },
    standard: "MNT-FAN-006 Rev 3",
    approvedOffset: "4.5 mm/s RMS",
    imageUrl: "/equipment/ct7801_cooling_tower_fan.svg",
    components: [
      {
        name: "composite drive shaft",
        category: "power transmission",
        relevance: "high",
        box: { left: 320, top: 200, right: 540, bottom: 330 },
        description: "Carbon-fiber composite floating drive shaft connecting driver motor to right-angle fan gearbox.",
        records: [
          {
            source: "WO-240169",
            type: "Work Order",
            summary: "Replaced drive-shaft coupling, aligned, dynamic vibration run.",
          },
        ],
      },
      {
        name: "fan blade assembly",
        category: "aero rotor",
        relevance: "high",
        box: { left: 100, top: 80, right: 800, bottom: 220 },
        description: "6-blade variable pitch FRP cooling tower fan rotor with hub clamp assembly.",
        records: [
          {
            source: "WO-240163",
            type: "Work Order",
            summary: "Leading-edge erosion on one FRP blade caused aerodynamic unbalance.",
          },
        ],
      },
      {
        name: "fan gearbox",
        category: "gear reducer",
        relevance: "moderate",
        box: { left: 400, top: 260, right: 560, bottom: 420 },
        description: "Right-angle bevel-helical gearbox (ratio 6.2:1) driving vertical fan shaft.",
        records: [
          {
            source: "WO-240164",
            type: "Work Order",
            summary: "TSHH-7803 oil temperature rising; cleaned oil cooler and replenished ISO VG 220.",
          },
        ],
      },
    ],
    initialResult: {
      incident: {
        asset_id: "CT-7801",
        equipment_type: "Cooling Tower Fan",
        symptom: "abnormal vibration on drive-shaft coupling",
        context: "after composite coupling replacement",
      },
      observations: [
        {
          id: "WO-240169",
          source: "WO-240169",
          document_type: "work_order",
          content: "Composite shaft coupling replaced. Vibration reading elevated on drive end.",
          relevance: "20",
        },
      ],
      evidence: [
        {
          id: "WO-240169",
          source: "WO-240169",
          document_type: "work_order",
          content: "Drive-shaft coupling replaced due to wear. Alignment checked.",
          relevance: "20",
        },
        {
          id: "WO-240163",
          source: "WO-240163",
          document_type: "work_order",
          content: "VSHH-7802 trip: leading-edge blade erosion caused 1X rotational unbalance.",
          relevance: "17",
        },
        {
          id: "MNT-FAN-006-Rev3",
          source: "MNT-FAN-006-Rev3",
          document_type: "procedure",
          content: "Status: CURRENT. Maximum allowable vibration velocity: 4.5 mm/s RMS overall.",
          relevance: "12",
          status: "CURRENT",
          revision: 3,
        },
      ],
      relevant_evidence: [],
      revision_checks: [],
      conflicts: [],
      hypotheses: [
        {
          id: "H1",
          title: "Drive-shaft angular misalignment across floating shaft",
          status: "strong",
          supporting_evidence: ["WO-240169"],
          contradicting_evidence: [],
          missing_evidence: ["Dial indicator reading on gearbox and motor shaft hubs"],
          confirmed: false,
        },
        {
          id: "H2",
          title: "FRP blade aerodynamic unbalance (WO-240163 pattern)",
          status: "moderate",
          supporting_evidence: ["WO-240163"],
          contradicting_evidence: [],
          missing_evidence: ["Blade tip track and pitch angle measurement"],
          confirmed: false,
        },
      ],
      missing_information: [
        "Laser alignment report for floating composite shaft",
        "Vibration FFT spectrum showing 1X vs 2X shaft frequency",
      ],
      investigation_steps: [
        "1. Measure floating shaft angular and parallel offset using laser alignment kit",
        "2. Inspect fan blade tip clearance and verify identical pitch angles (target: 14.5 deg)",
        "3. Check gearbox oil temperature and inspect magnetic drain plug",
      ],
      claims: [
        {
          id: "CLM-001",
          text: "Drive shaft alignment must be verified per MNT-FAN-006 Rev 3 before re-commissioning.",
          type: "procedural_requirement",
          supporting_sources: ["MNT-FAN-006-Rev3"],
          applicability_status: "exact asset standard",
          revision_warning: null,
          status: "supported",
        },
      ],
      trace: [
        { type: "incident_parsed", message: "Asset CT-7801 identified — drive-shaft coupling vibration" },
        { type: "evidence_search", message: "Found 27 completed maintenance records for CT-7801" },
        { type: "historical_match", message: "Correlated WO-240169 coupling with WO-240163 blade unbalance" },
      ],
      ai_synthesis_status: "active",
    },
  },

  "KC-4501": {
    tag: "KC-4501",
    name: "Recycle Gas Compressor",
    equipmentType: "Centrifugal Compressor (Multi-Stage)",
    area: "Reaction Loop Recycle",
    investigationId: "inv_kc4501_init",
    problemStatement:
      "Recycle Gas Compressor KC-4501 has high thrust bearing temperature and axial displacement shift after seal gas filter change.",
    recentMaintenance: {
      wo: "WO-240142",
      date: "2025-02-11",
      summary: "Seal gas coalescing filter elements replaced; DP transmitter calibrated",
    },
    historicalAnalogue: {
      doc: "RCA-KC4501-02",
      summary: "Balance line differential pressure increase caused aerodynamic thrust overload",
    },
    standard: "ENG-MNT-CMP-008 Rev 5",
    approvedOffset: "0.12 mm float",
    imageUrl: "/equipment/kc4501_compressor.svg",
    components: [
      {
        name: "thrust bearing",
        category: "bearing assembly",
        relevance: "high",
        box: { left: 480, top: 180, right: 620, bottom: 360 },
        description: "Tilting-pad active/inactive thrust bearing assembly with dual RTDs per pad.",
        records: [
          {
            source: "RCA-KC4501-02",
            type: "Historical RCA",
            summary: "Thrust pad metal temperature reached 108 C during balance line restriction.",
          },
        ],
      },
      {
        name: "dry gas seal",
        category: "shaft seal",
        relevance: "high",
        box: { left: 360, top: 190, right: 480, bottom: 350 },
        description: "Tandem dry gas seal with intermediate nitrogen buffer labyrinth.",
        records: [
          {
            source: "WO-240142",
            type: "Work Order",
            summary: "Coalescing seal gas filters renewed per scheduled maintenance.",
          },
        ],
      },
    ],
    initialResult: {
      incident: {
        asset_id: "KC-4501",
        equipment_type: "Centrifugal Compressor",
        symptom: "thrust bearing high temp and axial displacement shift",
        context: "following seal gas filter change",
      },
      observations: [
        {
          id: "WO-240142",
          source: "WO-240142",
          document_type: "work_order",
          content: "Seal gas filter replaced. Thrust temperature rose +9 C post-startup.",
          relevance: "21",
        },
      ],
      evidence: [
        {
          id: "WO-240142",
          source: "WO-240142",
          document_type: "work_order",
          content: "Seal gas primary vent flow within limits; thrust bearing pad temp elevated.",
          relevance: "21",
        },
        {
          id: "RCA-KC4501-02",
          source: "RCA-KC4501-02",
          document_type: "root_cause_analysis",
          content: "Balance piston labyrinth fouling increased net thrust load towards suction.",
          relevance: "18",
        },
      ],
      relevant_evidence: [],
      revision_checks: [],
      conflicts: [],
      hypotheses: [
        {
          id: "H1",
          title: "Balance piston labyrinth seal differential pressure elevation",
          status: "strong",
          supporting_evidence: ["RCA-KC4501-02"],
          contradicting_evidence: [],
          missing_evidence: ["Balance line transmitter PDT-4508 differential reading"],
          confirmed: false,
        },
      ],
      missing_information: [
        "Bently Nevada proximity probe axial float reading",
        "Lube oil supply pressure and cooler outlet temperature",
      ],
      investigation_steps: [
        "1. Verify Bently Nevada axial position monitor channels A and B against calibration zero",
        "2. Record balance line differential pressure and compare against clean rotor baseline",
        "3. Check lube oil supply temperature to thrust collar",
      ],
      claims: [
        {
          id: "CLM-001",
          text: "Axial displacement warning requires immediate correlation with balance line delta P.",
          type: "investigation_hypothesis",
          supporting_sources: ["RCA-KC4501-02"],
          applicability_status: "exact compressor match",
          revision_warning: null,
          status: "supported",
        },
      ],
      trace: [
        { type: "incident_parsed", message: "Asset KC-4501 identified — thrust temp & axial shift" },
        { type: "historical_match", message: "Found RCA-KC4501-02 balance piston thrust anomaly" },
      ],
      ai_synthesis_status: "active",
    },
  },

  "DC-3401A": {
    tag: "DC-3401A",
    name: "Catalyst Reduction Reactor",
    equipmentType: "Fixed-Bed Catalytic Reactor",
    area: "Catalyst Preparation",
    investigationId: "inv_dc3401a_init",
    problemStatement:
      "Catalyst Reduction Reactor DC-3401A has bed temperature discrepancy and N2 inert valve slow response after catalyst turnaround.",
    recentMaintenance: {
      wo: "WO-240056",
      date: "2024-07-11",
      summary: "Bed multipoint thermocouple point 3 replaced in sheath assembly",
    },
    historicalAnalogue: {
      doc: "WO-240059",
      summary: "Actuator seals hardened and positioner out of calibration on N2 inert valve",
    },
    standard: "SOP-CAT-3401 Rev 4",
    approvedOffset: "0.05 Nm3/h",
    imageUrl: "/equipment/dc3401a_reactor.svg",
    components: [
      {
        name: "multipoint thermocouple",
        category: "temperature sensor",
        relevance: "high",
        box: { left: 350, top: 120, right: 550, bottom: 380 },
        description: "8-point mineral insulated multipoint thermocouple array spanning catalyst bed depth.",
        records: [
          {
            source: "WO-240056",
            type: "Work Order",
            summary: "Replaced TC point 3 in multipoint assembly, verified TSHH-3401 interlock.",
          },
        ],
      },
    ],
    initialResult: {
      incident: {
        asset_id: "DC-3401A",
        equipment_type: "Catalytic Reactor",
        symptom: "bed temperature discrepancy and inert valve sluggish response",
        context: "post-turnaround operation",
      },
      observations: [
        {
          id: "WO-240056",
          source: "WO-240056",
          document_type: "work_order",
          content: "Bed thermocouple element 3 reading open circuit during reduction cycle.",
          relevance: "20",
        },
      ],
      evidence: [
        {
          id: "WO-240056",
          source: "WO-240056",
          document_type: "work_order",
          content: "Thermocouple replaced and interlock verified.",
          relevance: "20",
        },
        {
          id: "WO-240059",
          source: "WO-240059",
          document_type: "work_order",
          content: "N2 inert valve slow; actuator seals serviced and positioner calibrated.",
          relevance: "18",
        },
      ],
      relevant_evidence: [],
      revision_checks: [],
      conflicts: [],
      hypotheses: [
        {
          id: "H1",
          title: "Positioner air supply contamination or actuator seal degradation",
          status: "strong",
          supporting_evidence: ["WO-240059"],
          contradicting_evidence: [],
          missing_evidence: ["Stroking time test data under full supply pressure"],
          confirmed: false,
        },
      ],
      missing_information: ["Loop resistance measurement of multipoint thermocouple channels"],
      investigation_steps: [
        "1. Perform loop resistance check on multipoint thermocouple terminal head",
        "2. Stroke N2 inert valve and record opening/closing time",
      ],
      claims: [
        {
          id: "CLM-001",
          text: "Inert valve stroking time must satisfy safety interlock SEQ-3401 criteria.",
          type: "procedural_requirement",
          supporting_sources: ["WO-240059"],
          applicability_status: "exact asset and interlock match",
          revision_warning: null,
          status: "supported",
        },
      ],
      trace: [
        { type: "incident_parsed", message: "Asset DC-3401A identified — bed temp & valve response" },
        { type: "historical_match", message: "Found WO-240056 & WO-240059 matching failure pattern" },
      ],
      ai_synthesis_status: "active",
    },
  },
  "FA-8901": {
    tag: "FA-8901",
    name: "Reflux Accumulator Drum",
    equipmentType: "Horizontal Vessel / Drum",
    area: "Distillation System",
    investigationId: "inv_fa8901_init",
    problemStatement:
      "Reflux drum FA-8901 level tracking anomaly and erratic LT reading following sensing line service. What should the engineer investigate?",
    recentMaintenance: {
      wo: "WO-240193",
      date: "2025-04-06",
      summary: "Level bridle did not track; bridle legs plugged with polymer fines cleared.",
    },
    historicalAnalogue: {
      doc: "WO-240196",
      summary: "Pressure-transmitter impulse line plugged with fines; cleared and re-zeroed PT-8902.",
    },
    standard: "ENG-STD-INST-082 Rev 3",
    approvedOffset: "± 1.0% span",
    imageUrl: "/equipment/fa8901_reflux_drum.svg",
    components: [
      {
        name: "level bridle",
        category: "level instrument assembly",
        relevance: "high",
        box: { left: 180, top: 120, right: 380, bottom: 420 },
        description: "External level bridle housing radar/displacer level transmitter and isolation root valves.",
        records: [
          {
            source: "WO-240193",
            type: "Work Order",
            summary: "Bridle isolation legs flushed to clear polymer-fines blockage.",
          },
        ],
      },
      {
        name: "impulse line",
        category: "sensing path",
        relevance: "high",
        box: { left: 400, top: 180, right: 600, bottom: 350 },
        description: "Differential pressure impulse tubing connecting drum vapor and liquid taps to transmitter manifold.",
        records: [
          {
            source: "WO-240196",
            type: "Historical Record",
            summary: "Impulse tubing rodded and purged with nitrogen to restore transmitter tracking.",
          },
        ],
      },
      {
        name: "drum shell",
        category: "pressure containment",
        relevance: "secondary",
        box: { left: 150, top: 100, right: 750, bottom: 450 },
        description: "Horizontal carbon steel pressure vessel operating under solvent reflux condensation conditions.",
        records: [
          {
            source: "WO-240196",
            type: "Asset Record",
            summary: "FA-8901 operational envelope and relief set-points verified.",
          },
        ],
      },
    ],
    initialResult: {
      incident: {
        asset_id: "FA-8901",
        equipment_type: "Reflux Accumulator Drum",
        symptom: "level indication mismatch and stagnant transmitter tracking",
        context: "following sensing-line flush and turnaround restart",
      },
      observations: [
        {
          id: "WO-240193",
          source: "WO-240193",
          document_type: "work_order",
          content: "Level bridle did not track; bridle legs plugged with fines.",
          relevance: "22",
        },
      ],
      evidence: [
        {
          id: "WO-240193",
          source: "WO-240193",
          document_type: "work_order",
          content: "Bridle isolation legs flushed and cleared of polymer fines.",
          relevance: "22",
        },
        {
          id: "WO-240196",
          source: "WO-240196",
          document_type: "work_order",
          content: "PT-8902 impulse line cleared of fine deposits and re-zeroed.",
          relevance: "19",
        },
      ],
      relevant_evidence: [],
      revision_checks: [],
      conflicts: [],
      hypotheses: [
        {
          id: "H1",
          title: "Sensing bridle impulse path restriction by polymer fines",
          status: "strong",
          supporting_evidence: ["WO-240193", "WO-240196"],
          contradicting_evidence: [],
          missing_evidence: ["Differential pressure validation across root valves"],
          confirmed: false,
        },
      ],
      missing_information: ["Bridle root valve blow-through verification", "Hydrostatic test of transmitter sensing leg"],
      investigation_steps: [
        "1. Check level transmitter against sight glass reading to verify disparity",
        "2. Blow through sensing impulse lines with dry nitrogen",
        "3. Verify transmitter zero with equalizing valve open",
      ],
      claims: [
        {
          id: "CLM-001",
          text: "Sensing path blockage is the historically validated primary cause of level tracking failure on FA-8901.",
          type: "investigation_hypothesis",
          supporting_sources: ["WO-240193", "WO-240196"],
          applicability_status: "exact asset and service match",
          revision_warning: null,
          status: "supported",
        },
      ],
      trace: [
        { type: "incident_parsed", message: "Asset FA-8901 identified — level bridle tracking error" },
        { type: "historical_match", message: "Found WO-240193 & WO-240196 matching sensing line fines pattern" },
      ],
      ai_synthesis_status: "active",
    },
  },
  "LV-6701": {
    tag: "LV-6701",
    name: "Level Control Valve",
    equipmentType: "Globe Control Valve",
    area: "Polymer Separation",
    investigationId: "inv_lv6701_init",
    problemStatement:
      "Control valve LV-6701 unresponsive and stem sticking after PTFE packing replacement. What should the engineer investigate?",
    recentMaintenance: {
      wo: "WO-240135",
      date: "2025-01-06",
      summary: "Valve unresponsive; stem seized in PTFE packing from over-tightening plus polymer fines.",
    },
    historicalAnalogue: {
      doc: "WO-240138",
      summary: "PTFE V-ring stem packing worn; renewed packing set and re-torqued gland.",
    },
    standard: "VALVE-MNT-034 Rev 2",
    approvedOffset: "Stem friction < 150 N",
    imageUrl: "/equipment/lv6701_control_valve.svg",
    components: [
      {
        name: "valve stem & packing",
        category: "valve internals",
        relevance: "high",
        box: { left: 320, top: 160, right: 580, bottom: 380 },
        description: "Hardened stainless steel stem running through live-loaded PTFE chevron V-ring packing box.",
        records: [
          {
            source: "WO-240135",
            type: "Work Order",
            summary: "Stem seized due to overtightened gland bolts and polymer fines ingress.",
          },
          {
            source: "WO-240138",
            type: "Work Order",
            summary: "Renewed PTFE V-ring set; gland torqued to revised engineering limit.",
          },
        ],
      },
      {
        name: "pneumatic actuator",
        category: "valve driver",
        relevance: "high",
        box: { left: 280, top: 40, right: 620, bottom: 220 },
        description: "Diaphragm actuator providing linear positioning force against heavy internal springs.",
        records: [
          {
            source: "WO-240135",
            type: "Work Order",
            summary: "Actuator bench set and spring pre-compression verified.",
          },
        ],
      },
    ],
    initialResult: {
      incident: {
        asset_id: "LV-6701",
        equipment_type: "Globe Control Valve",
        symptom: "valve stem sticking and slow stroking speed",
        context: "following stem packing replacement",
      },
      observations: [
        {
          id: "WO-240135",
          source: "WO-240135",
          document_type: "work_order",
          content: "Stem seized in PTFE packing from over-tightening plus polymer fines.",
          relevance: "24",
        },
      ],
      evidence: [
        {
          id: "WO-240135",
          source: "WO-240135",
          document_type: "work_order",
          content: "Valve stem friction exceeded actuator output after excessive gland torque.",
          relevance: "24",
        },
        {
          id: "WO-240138",
          source: "WO-240138",
          document_type: "work_order",
          content: "PTFE V-ring stem packing renewal procedure and correct torque requirements.",
          relevance: "20",
        },
      ],
      relevant_evidence: [],
      revision_checks: [],
      conflicts: [],
      hypotheses: [
        {
          id: "H1",
          title: "Excessive gland packing torque causing stem binding",
          status: "strong",
          supporting_evidence: ["WO-240135", "WO-240138"],
          contradicting_evidence: [],
          missing_evidence: ["As-found gland bolt torque readings"],
          confirmed: false,
        },
      ],
      missing_information: ["Field gland nut torque check", "Positioner air output pressure vs actuator bench set"],
      investigation_steps: [
        "1. Check gland follower bolt torque with calibrated torque wrench",
        "2. Inspect visible stem travel for scoring or polymer fines build-up",
        "3. Perform open/close stroking test using digital valve controller diagnostic routine",
      ],
      claims: [
        {
          id: "CLM-001",
          text: "Over-tightening of PTFE packing is the verified root cause of stem seizure on LV-6701.",
          type: "investigation_hypothesis",
          supporting_sources: ["WO-240135"],
          applicability_status: "exact asset and valve trim match",
          revision_warning: null,
          status: "supported",
        },
      ],
      trace: [
        { type: "incident_parsed", message: "Asset LV-6701 identified — stem seizure & packing torque" },
        { type: "historical_match", message: "Found WO-240135 & WO-240138 confirming packing friction failure" },
      ],
      ai_synthesis_status: "active",
    },
  },
  "YD-2301": {
    tag: "YD-2301",
    name: "Polymer Fluid Bed Dryer",
    equipmentType: "Fluid Bed Dryer Assembly",
    area: "Drying System",
    investigationId: "inv_yd2301_init",
    problemStatement:
      "Fluid bed dryer YD-2301 experiencing powder and steam leak at discharge gland after packing overhaul. What should the engineer investigate?",
    recentMaintenance: {
      wo: "WO-240028",
      date: "2025-03-03",
      summary: "Steam and powder leak at discharge gland; PTFE 4526L packing worn beyond limit.",
    },
    historicalAnalogue: {
      doc: "WO-240029",
      summary: "Feed-end PTFE 4505L packing hardened and worn; renewed two feed-end packing pieces.",
    },
    standard: "MNT-DRY-2301 Rev 3",
    approvedOffset: "Zero powder leakage",
    imageUrl: "/equipment/yd2301_dryer.svg",
    components: [
      {
        name: "discharge gland packing",
        category: "shaft seal assembly",
        relevance: "high",
        box: { left: 520, top: 180, right: 780, bottom: 400 },
        description: "High-temperature PTFE 4526L braided gland packing rings sealing dryer rotary discharge shaft.",
        records: [
          {
            source: "WO-240028",
            type: "Work Order",
            summary: "Discharge gland renewed with PTFE 4526L packing; torque checked per procedure.",
          },
        ],
      },
      {
        name: "feed-end packing",
        category: "shaft seal assembly",
        relevance: "moderate",
        box: { left: 120, top: 180, right: 360, bottom: 400 },
        description: "Feed-end PTFE 4505L shaft packing preventing powder ingress into external bearings.",
        records: [
          {
            source: "WO-240029",
            type: "Work Order",
            summary: "Feed-end packing renewed after hardening from localized process heat.",
          },
        ],
      },
    ],
    initialResult: {
      incident: {
        asset_id: "YD-2301",
        equipment_type: "Fluid Bed Dryer Assembly",
        symptom: "steam and polymer powder leakage at discharge end",
        context: "following packing replacement during quarterly turnaround",
      },
      observations: [
        {
          id: "WO-240028",
          source: "WO-240028",
          document_type: "work_order",
          content: "Steam and powder leak at discharge gland; PTFE 4526L packing worn beyond limit.",
          relevance: "23",
        },
      ],
      evidence: [
        {
          id: "WO-240028",
          source: "WO-240028",
          document_type: "work_order",
          content: "Discharge gland packing wear caused steam escape and powder carryover.",
          relevance: "23",
        },
        {
          id: "WO-240029",
          source: "WO-240029",
          document_type: "work_order",
          content: "Feed-end packing hardening history and gland adjustment criteria.",
          relevance: "19",
        },
      ],
      relevant_evidence: [],
      revision_checks: [],
      conflicts: [],
      hypotheses: [
        {
          id: "H1",
          title: "Incorrect packing ring material specification (4505L vs 4526L) or uneven gland torque",
          status: "strong",
          supporting_evidence: ["WO-240028", "WO-240029"],
          contradicting_evidence: [],
          missing_evidence: ["Shaft sleeve runout and surface roughness measurement"],
          confirmed: false,
        },
      ],
      missing_information: ["Verification of packing material code installed on discharge gland", "Shaft radial runout reading"],
      investigation_steps: [
        "1. Confirm packing material installed is PTFE 4526L (high-temp) rather than feed-end 4505L",
        "2. Check gland follower alignment for cocking and uneven bolt tension",
        "3. Inspect shaft sleeve for grooving or abrasive polymer powder scoring",
      ],
      claims: [
        {
          id: "CLM-001",
          text: "Discharge gland requires PTFE 4526L specification to withstand combined steam temperature and fine polymer powder.",
          type: "investigation_hypothesis",
          supporting_sources: ["WO-240028"],
          applicability_status: "exact asset and gland location match",
          revision_warning: null,
          status: "supported",
        },
      ],
      trace: [
        { type: "incident_parsed", message: "Asset YD-2301 identified — discharge gland steam & powder leak" },
        { type: "historical_match", message: "Found WO-240028 & WO-240029 confirming gland packing failure history" },
      ],
      ai_synthesis_status: "active",
    },
  },
};

export function getEquipmentTroubleshooting(assetTag?: string | null): EquipmentTroubleshootingConfig {
  if (!assetTag) return equipmentTroubleshootingConfigs["P-101"]!;
  const cleaned = assetTag.trim().toUpperCase();
  if (equipmentTroubleshootingConfigs[cleaned]) {
    return equipmentTroubleshootingConfigs[cleaned]!;
  }
  // Generic fallback if an unknown tag is passed
  return {
    tag: cleaned,
    name: `${cleaned} Process Equipment`,
    equipmentType: "Process Equipment",
    area: "LLDPE Operations",
    investigationId: `inv_${cleaned.toLowerCase().replace(/[^a-z0-9]/g, "")}_init`,
    problemStatement: `${cleaned} has reported operational deviations following recent maintenance. What should the engineer investigate?`,
    recentMaintenance: {
      wo: `WO-${cleaned}-01`,
      date: "2025-01-15",
      summary: "Scheduled routine maintenance and inspection completed.",
    },
    historicalAnalogue: {
      doc: `RCA-${cleaned}`,
      summary: "Historical operational discrepancy recorded in unit memory log.",
    },
    standard: "ENG-STD-014 Rev 4",
    approvedOffset: "Within OEM limits",
    imageUrl: "/pump_p101_assembly.jpg",
    components: [
      {
        name: "primary assembly",
        category: "core",
        relevance: "high",
        box: { left: 200, top: 150, right: 650, bottom: 420 },
        description: `Core mechanical assembly for asset ${cleaned}.`,
        records: [
          {
            source: `WO-${cleaned}`,
            type: "Maintenance Log",
            summary: `Operating records for ${cleaned}.`,
          },
        ],
      },
    ],
    initialResult: {
      incident: {
        asset_id: cleaned,
        equipment_type: "Process Equipment",
        symptom: "operational deviation",
        context: "following recent maintenance",
      },
      observations: [],
      evidence: [],
      relevant_evidence: [],
      revision_checks: [],
      conflicts: [],
      hypotheses: [
        {
          id: "H1",
          title: `Operational deviation on ${cleaned}`,
          status: "moderate",
          supporting_evidence: [],
          contradicting_evidence: [],
          missing_evidence: ["Current field operating parameters"],
          confirmed: false,
        },
      ],
      missing_information: ["Current field measurements", "Operating telemetry"],
      investigation_steps: [
        `1. Inspect physical condition of ${cleaned} and compare against baseline`,
        "2. Review recent work orders and verify procedure currency",
      ],
      claims: [
        {
          id: "CLM-001",
          text: `Investigation initiated for asset ${cleaned}.`,
          type: "investigation_hypothesis",
          supporting_sources: [],
          applicability_status: "exact asset match",
          revision_warning: null,
          status: "supported",
        },
      ],
      trace: [
        { type: "incident_parsed", message: `Asset ${cleaned} identified — operational deviation` },
      ],
      ai_synthesis_status: "active",
    },
  };
}

