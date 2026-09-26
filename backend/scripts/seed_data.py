"""
OmniCivic AI — Deterministic Seed Data Generator
Generates 50 citizen reports across 5-10 wards with 4 guaranteed demo scenarios.
Run: python -m backend.scripts.seed_data (from project root)
"""

import json
import os
from datetime import datetime

# ─── Paths ──────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


# ─── Ward definitions (fictional Indian city wards) ────────────────────────────

WARDS = {
    "Ward 1 - Colaba": {"center": (19.0250, 72.8350)},
    "Ward 2 - Fort": {"center": (19.0320, 72.8420)},
    "Ward 3 - Marine Lines": {"center": (19.0760, 72.8780)},
    "Ward 4 - Grant Road": {"center": (19.0650, 72.8600)},
    "Ward 5 - Bandra West": {"center": (19.0540, 72.8400)},
    "Ward 6 - Kurla": {"center": (19.0900, 72.8500)},
    "Ward 7 - Andheri East": {"center": (19.1190, 72.8470)},
    "Ward 8 - Goregaon": {"center": (19.1300, 72.8600)},
    "Ward 9 - Borivali": {"center": (19.1400, 72.8700)},
    "Ward 10 - Thane Border": {"center": (19.1500, 72.8800)},
}

# ─── Citizen names for realistic reports ────────────────────────────────────────

CITIZEN_NAMES = [
    "Rajesh Kumar", "Priya Sharma", "Amit Patel", "Sunita Deshpande",
    "Vikram Singh", "Meera Nair", "Suresh Joshi", "Anita Kulkarni",
    "Manoj Gupta", "Kavita Iyer", "Deepak Verma", "Lakshmi Rao",
    "Ramesh Patil", "Pooja Mehta", "Sanjay Tiwari", "Neha Desai",
    "Arun Bhat", "Rekha Pillai", "Ganesh Sawant", "Divya Menon",
    "Harish Reddy", "Swati Jain", "Mukesh Yadav", "Preeti Saxena",
    "Kiran Naik", "Asha Bhosle", "Nitin Chavan", "Ritu Agarwal",
    "Sunil More", "Anjali Kapoor", "Venkat Rao", "Smita Kulkarni",
    "Pramod Shirke", "Suman Gaikwad", "Ajay Mane", "Pallavi Datar",
    "Yogesh Pawar", "Manisha Raut", "Tushar Joshi", "Leela Hegde",
    "Ashok Jadhav", "Nandini Bose", "Vishal Shetty", "Uma Maheshwari",
    "Rahul Khare", "Sarita Pardeshi", "Dinesh Solanki", "Madhuri Gokhale",
    "Satish Bhagat", "Geeta Mishra",
]


# ─── Scenario 1: Water leakage → Road damage → Pothole → Waterlogging ─────────
# Ward 7 - Andheri East, radius ~150m, July 1-4

SCENARIO_1_REPORTS = [
    {
        "report_id": "CIV-2026-1001",
        "timestamp": "2026-07-01T08:30:00+05:30",
        "citizen_name": "Rajesh Kumar",
        "phone": "+91-98200-10001",
        "location": {"latitude": 19.1190, "longitude": 72.8470, "address": "Near Chakala Junction, Andheri East", "ward": "Ward 7 - Andheri East"},
        "description": "There is a major water leak from the underground pipe near Chakala junction. Water has been flowing continuously for 2 days now. The road is getting soaked and there is water everywhere. Please send someone urgently.",
        "image_filename": "leak_01.jpg",
        "status": "SUBMITTED",
        "ward": "Ward 7 - Andheri East",
        "scenario_id": 1,
    },
    {
        "report_id": "CIV-2026-1002",
        "timestamp": "2026-07-01T14:15:00+05:30",
        "citizen_name": "Priya Sharma",
        "phone": "+91-98200-10002",
        "location": {"latitude": 19.1192, "longitude": 72.8472, "address": "Chakala Junction Main Road, Andheri East", "ward": "Ward 7 - Andheri East"},
        "description": "The road surface near Chakala junction has started cracking badly. I think the water leak from the pipe underneath is causing the road to break apart. Vehicles are having difficulty passing through. Very dangerous for two-wheelers.",
        "image_filename": "road_damage_01.jpg",
        "status": "SUBMITTED",
        "ward": "Ward 7 - Andheri East",
        "scenario_id": 1,
    },
    {
        "report_id": "CIV-2026-1003",
        "timestamp": "2026-07-02T09:00:00+05:30",
        "citizen_name": "Amit Patel",
        "phone": "+91-98200-10003",
        "location": {"latitude": 19.1188, "longitude": 72.8468, "address": "Opposite Star Mall, Andheri East", "ward": "Ward 7 - Andheri East"},
        "description": "A large pothole has formed on the main road opposite Star Mall. It is almost 2 feet deep and filled with muddy water. Yesterday a scooter rider fell into it and got injured. This needs immediate attention.",
        "image_filename": "pothole_01.jpg",
        "status": "SUBMITTED",
        "ward": "Ward 7 - Andheri East",
        "scenario_id": 1,
    },
    {
        "report_id": "CIV-2026-1004",
        "timestamp": "2026-07-02T16:30:00+05:30",
        "citizen_name": "Sunita Deshpande",
        "phone": "+91-98200-10004",
        "location": {"latitude": 19.1191, "longitude": 72.8469, "address": "Chakala Signal Road, Andheri East", "ward": "Ward 7 - Andheri East"},
        "description": "Severe waterlogging on Chakala road after just light rain. The water is not draining at all. It looks like the road damage and potholes are trapping water. Buses and autos are stuck. Ankle-deep water for pedestrians.",
        "image_filename": "waterlogging_01.jpg",
        "status": "SUBMITTED",
        "ward": "Ward 7 - Andheri East",
        "scenario_id": 1,
    },
    {
        "report_id": "CIV-2026-1005",
        "timestamp": "2026-07-03T10:00:00+05:30",
        "citizen_name": "Vikram Singh",
        "phone": "+91-98200-10005",
        "location": {"latitude": 19.1193, "longitude": 72.8471, "address": "Near Andheri East Metro Station", "ward": "Ward 7 - Andheri East"},
        "description": "The water pipe is still leaking near Chakala! Nobody has come to fix it. I submitted a complaint 2 days ago. The water is now spreading to the metro station area. Please escalate this.",
        "image_filename": "leak_02.jpg",
        "status": "SUBMITTED",
        "ward": "Ward 7 - Andheri East",
        "scenario_id": 1,
    },
    {
        "report_id": "CIV-2026-1006",
        "timestamp": "2026-07-03T11:30:00+05:30",
        "citizen_name": "Meera Nair",
        "phone": "+91-98200-10006",
        "location": {"latitude": 19.1187, "longitude": 72.8473, "address": "Service Road near Chakala, Andheri East", "ward": "Ward 7 - Andheri East"},
        "description": "The service road near Chakala is completely damaged. There are cracks everywhere and the road surface is crumbling. This happened after the water leak started last week. Please repair the road before monsoon season makes it worse.",
        "image_filename": "road_damage_02.jpg",
        "status": "SUBMITTED",
        "ward": "Ward 7 - Andheri East",
        "scenario_id": 1,
    },
]

# ─── Scenario 2: Drain blockage → Waterlogging → Garbage accumulation ──────────
# Ward 12 → using Ward 6 - Kurla, radius ~150m, July 2-5

SCENARIO_2_REPORTS = [
    {
        "report_id": "CIV-2026-1007",
        "timestamp": "2026-07-02T07:00:00+05:30",
        "citizen_name": "Suresh Joshi",
        "phone": "+91-98200-10007",
        "location": {"latitude": 19.0720, "longitude": 72.8560, "address": "Tilak Nagar Market Road, Kurla", "ward": "Ward 6 - Kurla"},
        "description": "The main drain in Tilak Nagar market area is completely blocked. I can see plastic waste and construction debris clogging the drain mouth. Water is already starting to accumulate on the road even without rain.",
        "image_filename": "drain_01.jpg",
        "status": "SUBMITTED",
        "ward": "Ward 6 - Kurla",
        "scenario_id": 2,
    },
    {
        "report_id": "CIV-2026-1008",
        "timestamp": "2026-07-02T15:00:00+05:30",
        "citizen_name": "Anita Kulkarni",
        "phone": "+91-98200-10008",
        "location": {"latitude": 19.0722, "longitude": 72.8562, "address": "Behind Tilak Nagar Market, Kurla", "ward": "Ward 6 - Kurla"},
        "description": "Heavy waterlogging behind Tilak Nagar market. The blocked drain is causing all the water to stay on the road. Shopkeepers are unable to open their shops. Water is entering ground floor homes.",
        "image_filename": "waterlogging_02.jpg",
        "status": "SUBMITTED",
        "ward": "Ward 6 - Kurla",
        "scenario_id": 2,
    },
    {
        "report_id": "CIV-2026-1009",
        "timestamp": "2026-07-03T08:30:00+05:30",
        "citizen_name": "Manoj Gupta",
        "phone": "+91-98200-10009",
        "location": {"latitude": 19.0719, "longitude": 72.8558, "address": "Tilak Nagar Colony, Kurla", "ward": "Ward 6 - Kurla"},
        "description": "Garbage is piling up near the blocked drain. The collection truck has not come for 3 days. The waterlogging is mixing with the garbage creating a terrible smell. Health hazard for residents.",
        "image_filename": "garbage_01.jpg",
        "status": "SUBMITTED",
        "ward": "Ward 6 - Kurla",
        "scenario_id": 2,
    },
    {
        "report_id": "CIV-2026-1010",
        "timestamp": "2026-07-03T12:00:00+05:30",
        "citizen_name": "Kavita Iyer",
        "phone": "+91-98200-10010",
        "location": {"latitude": 19.0723, "longitude": 72.8561, "address": "Near Tilak Nagar Bus Stop, Kurla", "ward": "Ward 6 - Kurla"},
        "description": "Another drain near the bus stop is also getting blocked now. The garbage from the waterlogged area is floating and entering this drain too. Situation is getting worse every day.",
        "image_filename": "drain_02.jpg",
        "status": "SUBMITTED",
        "ward": "Ward 6 - Kurla",
        "scenario_id": 2,
    },
    {
        "report_id": "CIV-2026-1011",
        "timestamp": "2026-07-04T09:00:00+05:30",
        "citizen_name": "Deepak Verma",
        "phone": "+91-98200-10011",
        "location": {"latitude": 19.0721, "longitude": 72.8563, "address": "Tilak Nagar Main Road, Kurla", "ward": "Ward 6 - Kurla"},
        "description": "Stagnant water on Tilak Nagar main road for the 3rd day. It is turning green and mosquitoes are breeding. Children in the area are falling sick. Dengue risk is very high. Please take action immediately.",
        "image_filename": "waterlogging_03.jpg",
        "status": "SUBMITTED",
        "ward": "Ward 6 - Kurla",
        "scenario_id": 2,
    },
]

# ─── Scenario 3: Exposed wire near school — low count, critical impact ──────────
# Ward 3 - Marine Lines, 2 reports only

SCENARIO_3_REPORTS = [
    {
        "report_id": "CIV-2026-1012",
        "timestamp": "2026-07-05T07:45:00+05:30",
        "citizen_name": "Lakshmi Rao",
        "phone": "+91-98200-10012",
        "location": {"latitude": 19.0760, "longitude": 72.8780, "address": "Near St. Xavier's School Gate, Marine Lines", "ward": "Ward 3 - Marine Lines"},
        "description": "URGENT: There are exposed electrical wires hanging from a broken pole right next to St. Xavier's School gate. Children walk past this every morning. One wire is almost touching the ground. This is extremely dangerous, especially during rain. Someone could die.",
        "image_filename": "exposed_wire_01.jpg",
        "status": "SUBMITTED",
        "ward": "Ward 3 - Marine Lines",
        "scenario_id": 3,
    },
    {
        "report_id": "CIV-2026-1013",
        "timestamp": "2026-07-05T08:15:00+05:30",
        "citizen_name": "Ramesh Patil",
        "phone": "+91-98200-10013",
        "location": {"latitude": 19.0762, "longitude": 72.8782, "address": "School Lane, Marine Lines", "ward": "Ward 3 - Marine Lines"},
        "description": "Broken streetlight on School Lane has exposed wires. The insulation has completely worn off. This is right on the path children use to go to school. With monsoon approaching, live wires and water is a deadly combination. Needs emergency response.",
        "image_filename": "exposed_wire_02.jpg",
        "status": "SUBMITTED",
        "ward": "Ward 3 - Marine Lines",
        "scenario_id": 3,
    },
]

# ─── Scenario 4: Repeated pothole after claimed resolution ──────────────────────
# Ward 5 - Bandra West, June 20 - July 5 (spans resolution attempt)

SCENARIO_4_REPORTS = [
    {
        "report_id": "CIV-2026-1014",
        "timestamp": "2026-06-20T10:00:00+05:30",
        "citizen_name": "Pooja Mehta",
        "phone": "+91-98200-10014",
        "location": {"latitude": 19.0540, "longitude": 72.8400, "address": "Hill Road, Bandra West", "ward": "Ward 5 - Bandra West"},
        "description": "Large pothole on Hill Road near the signal. Getting bigger every day with the rains. Multiple vehicles have been damaged. Two-wheelers especially at risk. Please fill and repair this urgently.",
        "image_filename": "pothole_02.jpg",
        "status": "SUBMITTED",
        "ward": "Ward 5 - Bandra West",
        "scenario_id": 4,
    },
    {
        "report_id": "CIV-2026-1015",
        "timestamp": "2026-06-25T14:00:00+05:30",
        "citizen_name": "Sanjay Tiwari",
        "phone": "+91-98200-10015",
        "location": {"latitude": 19.0541, "longitude": 72.8401, "address": "Hill Road Signal, Bandra West", "ward": "Ward 5 - Bandra West"},
        "description": "The pothole on Hill Road I reported 5 days ago has not been fixed. It is now even deeper. Today a delivery boy on a bike fell and fractured his hand. How many injuries will it take before action is taken?",
        "image_filename": "pothole_03.jpg",
        "status": "SUBMITTED",
        "ward": "Ward 5 - Bandra West",
        "scenario_id": 4,
    },
    {
        "report_id": "CIV-2026-1016",
        "timestamp": "2026-07-03T09:30:00+05:30",
        "citizen_name": "Neha Desai",
        "phone": "+91-98200-10016",
        "location": {"latitude": 19.0540, "longitude": 72.8400, "address": "Hill Road, Bandra West", "ward": "Ward 5 - Bandra West"},
        "description": "The pothole on Hill Road was supposedly repaired last week but the patch has already come off! The pothole is back and even bigger now. Poor quality repair work. Need proper permanent fix this time.",
        "image_filename": "pothole_04.jpg",
        "status": "SUBMITTED",
        "ward": "Ward 5 - Bandra West",
        "scenario_id": 4,
    },
    {
        "report_id": "CIV-2026-1017",
        "timestamp": "2026-07-05T11:00:00+05:30",
        "citizen_name": "Arun Bhat",
        "phone": "+91-98200-10017",
        "location": {"latitude": 19.0539, "longitude": 72.8402, "address": "Near Hill Road Junction, Bandra West", "ward": "Ward 5 - Bandra West"},
        "description": "Road around the pothole area on Hill Road is completely damaged now. The failed repair made things worse. Large chunks of road surface have broken off. The whole stretch of 20 meters needs resurfacing.",
        "image_filename": "pothole_05.jpg",
        "status": "SUBMITTED",
        "ward": "Ward 5 - Bandra West",
        "scenario_id": 4,
    },
]

# ─── Independent reports (33 scattered across wards) ────────────────────────────

INDEPENDENT_REPORTS = [
    {
        "report_id": "CIV-2026-1018",
        "timestamp": "2026-07-01T20:00:00+05:30",
        "citizen_name": "Rekha Pillai",
        "location": {"latitude": 19.0250, "longitude": 72.8350, "address": "Shahid Bhagat Singh Road, Colaba", "ward": "Ward 1 - Colaba"},
        "description": "Streetlight not working on SBS Road near Regal Cinema. The entire stretch is dark at night. Unsafe for women and elderly pedestrians.",
        "image_filename": "streetlight_01.jpg",
        "ward": "Ward 1 - Colaba",
    },
    {
        "report_id": "CIV-2026-1019",
        "timestamp": "2026-07-02T06:30:00+05:30",
        "citizen_name": "Ganesh Sawant",
        "location": {"latitude": 19.0255, "longitude": 72.8355, "address": "Colaba Market Lane", "ward": "Ward 1 - Colaba"},
        "description": "Garbage bins overflowing at Colaba Market. Stray dogs tearing through the bags. Waste scattered on the road. Needs daily collection, not alternate days.",
        "image_filename": "garbage_02.jpg",
        "ward": "Ward 1 - Colaba",
    },
    {
        "report_id": "CIV-2026-1020",
        "timestamp": "2026-07-01T09:00:00+05:30",
        "citizen_name": "Divya Menon",
        "location": {"latitude": 19.0320, "longitude": 72.8420, "address": "DN Road, Fort", "ward": "Ward 2 - Fort"},
        "description": "Sewage overflowing from manhole on DN Road. The smell is unbearable. Sewage water spreading on the road. Heritage area being polluted.",
        "image_filename": "sewage_01.jpg",
        "ward": "Ward 2 - Fort",
    },
    {
        "report_id": "CIV-2026-1021",
        "timestamp": "2026-07-03T13:00:00+05:30",
        "citizen_name": "Harish Reddy",
        "location": {"latitude": 19.0380, "longitude": 72.8480, "address": "Kala Ghoda Lane, Fort", "ward": "Ward 2 - Fort"},
        "description": "Pothole on Kala Ghoda road. Not very large but positioned right at a turn. Vehicles swerving to avoid it are creating more danger.",
        "image_filename": "pothole_06.jpg",
        "ward": "Ward 2 - Fort",
    },
    {
        "report_id": "CIV-2026-1022",
        "timestamp": "2026-07-02T11:00:00+05:30",
        "citizen_name": "Swati Jain",
        "location": {"latitude": 19.0650, "longitude": 72.8600, "address": "Grant Road Station Area", "ward": "Ward 4 - Grant Road"},
        "description": "Water leaking from pipe near Grant Road station footpath. Wasting clean water while people in the area face water shortage.",
        "image_filename": "leak_03.jpg",
        "ward": "Ward 4 - Grant Road",
    },
    {
        "report_id": "CIV-2026-1023",
        "timestamp": "2026-07-04T08:00:00+05:30",
        "citizen_name": "Mukesh Yadav",
        "location": {"latitude": 19.0680, "longitude": 72.8630, "address": "Lamington Road, Grant Road", "ward": "Ward 4 - Grant Road"},
        "description": "Road surface on Lamington Road damaged badly. Multiple cracks and the bitumen is peeling off. Heavy vehicles using this route daily making it worse.",
        "image_filename": "road_damage_03.jpg",
        "ward": "Ward 4 - Grant Road",
    },
    {
        "report_id": "CIV-2026-1024",
        "timestamp": "2026-07-01T12:00:00+05:30",
        "citizen_name": "Preeti Saxena",
        "location": {"latitude": 19.0900, "longitude": 72.8500, "address": "Kurla LBS Road", "ward": "Ward 6 - Kurla"},
        "description": "Drainage problem on LBS Road Kurla. Water not flowing out even after rain stopped 6 hours ago. Drain grating is too small or blocked internally.",
        "image_filename": "drainage_01.jpg",
        "ward": "Ward 6 - Kurla",
    },
    {
        "report_id": "CIV-2026-1025",
        "timestamp": "2026-07-03T15:00:00+05:30",
        "citizen_name": "Kiran Naik",
        "location": {"latitude": 19.0920, "longitude": 72.8520, "address": "Near Kurla Bus Depot", "ward": "Ward 6 - Kurla"},
        "description": "Waterlogging near Kurla bus depot. Buses unable to enter the depot. Passengers wading through knee-deep water to reach buses.",
        "image_filename": "waterlogging_04.jpg",
        "ward": "Ward 6 - Kurla",
    },
    {
        "report_id": "CIV-2026-1026",
        "timestamp": "2026-07-02T07:00:00+05:30",
        "citizen_name": "Asha Bhosle",
        "location": {"latitude": 19.1300, "longitude": 72.8600, "address": "Goregaon Market Road", "ward": "Ward 8 - Goregaon"},
        "description": "Garbage overflow at Goregaon market. The community bin has not been emptied for 4 days. Stench reaching nearby residential buildings.",
        "image_filename": "garbage_03.jpg",
        "ward": "Ward 8 - Goregaon",
    },
    {
        "report_id": "CIV-2026-1027",
        "timestamp": "2026-07-04T10:00:00+05:30",
        "citizen_name": "Nitin Chavan",
        "location": {"latitude": 19.1320, "longitude": 72.8620, "address": "Goregaon Link Road", "ward": "Ward 8 - Goregaon"},
        "description": "Sewage overflow on Goregaon Link Road near the nullah. Manhole cover dislodged and dirty water flowing on the road. Vehicles splashing it on pedestrians.",
        "image_filename": "sewage_02.jpg",
        "ward": "Ward 8 - Goregaon",
    },
    {
        "report_id": "CIV-2026-1028",
        "timestamp": "2026-07-01T21:00:00+05:30",
        "citizen_name": "Ritu Agarwal",
        "location": {"latitude": 19.1400, "longitude": 72.8700, "address": "Borivali Station Road", "ward": "Ward 9 - Borivali"},
        "description": "Three streetlights not working on Borivali station road. Very dark at night, especially near the underpass. Safety concern for commuters.",
        "image_filename": "streetlight_02.jpg",
        "ward": "Ward 9 - Borivali",
    },
    {
        "report_id": "CIV-2026-1029",
        "timestamp": "2026-07-03T14:00:00+05:30",
        "citizen_name": "Sunil More",
        "location": {"latitude": 19.1420, "longitude": 72.8720, "address": "Borivali West Main Road", "ward": "Ward 9 - Borivali"},
        "description": "Pothole near Borivali railway crossing. Auto rickshaws refusing to go through this road. Commuters forced to walk on damaged stretch.",
        "image_filename": "pothole_07.jpg",
        "ward": "Ward 9 - Borivali",
    },
    {
        "report_id": "CIV-2026-1030",
        "timestamp": "2026-07-02T08:00:00+05:30",
        "citizen_name": "Anjali Kapoor",
        "location": {"latitude": 19.1500, "longitude": 72.8800, "address": "Thane Border Road", "ward": "Ward 10 - Thane Border"},
        "description": "Water pipe leaking on Thane border road for past 1 week. Clean water being wasted. Puddle forming on the road causing traffic to slow down.",
        "image_filename": "leak_04.jpg",
        "ward": "Ward 10 - Thane Border",
    },
    {
        "report_id": "CIV-2026-1031",
        "timestamp": "2026-07-05T09:00:00+05:30",
        "citizen_name": "Venkat Rao",
        "location": {"latitude": 19.1520, "longitude": 72.8820, "address": "Industrial Area, Thane Border", "ward": "Ward 10 - Thane Border"},
        "description": "Exposed electrical wires near industrial area. Wire insulation melted due to overload. Workers passing by at risk. Factory owners have put up warning sign but wire still not fixed.",
        "image_filename": "exposed_wire_03.jpg",
        "ward": "Ward 10 - Thane Border",
    },
    {
        "report_id": "CIV-2026-1032",
        "timestamp": "2026-07-04T11:00:00+05:30",
        "citizen_name": "Smita Kulkarni",
        "location": {"latitude": 19.0260, "longitude": 72.8360, "address": "Navy Nagar Road, Colaba", "ward": "Ward 1 - Colaba"},
        "description": "Road damaged on Navy Nagar road. Heavy trucks from nearby construction site breaking the road surface daily. Speed breakers also damaged.",
        "image_filename": "road_damage_04.jpg",
        "ward": "Ward 1 - Colaba",
    },
    {
        "report_id": "CIV-2026-1033",
        "timestamp": "2026-07-05T07:30:00+05:30",
        "citizen_name": "Pramod Shirke",
        "location": {"latitude": 19.0910, "longitude": 72.8510, "address": "Kurla East Colony", "ward": "Ward 6 - Kurla"},
        "description": "Drain blocked in Kurla East colony. Debris from nearby construction has entered the drain. Water not flowing. Monsoon approaching and this will cause flooding.",
        "image_filename": "drain_03.jpg",
        "ward": "Ward 6 - Kurla",
    },
    {
        "report_id": "CIV-2026-1034",
        "timestamp": "2026-07-03T16:00:00+05:30",
        "citizen_name": "Suman Gaikwad",
        "location": {"latitude": 19.1310, "longitude": 72.8610, "address": "Goregaon East Highway Service Road", "ward": "Ward 8 - Goregaon"},
        "description": "Multiple potholes on the highway service road in Goregaon East. The stretch from Oberoi Mall to Aarey gate has at least 15 potholes.",
        "image_filename": "pothole_08.jpg",
        "ward": "Ward 8 - Goregaon",
    },
    {
        "report_id": "CIV-2026-1035",
        "timestamp": "2026-07-02T06:00:00+05:30",
        "citizen_name": "Ajay Mane",
        "location": {"latitude": 19.1410, "longitude": 72.8710, "address": "Borivali Market Lane", "ward": "Ward 9 - Borivali"},
        "description": "Garbage bins overflowing at Borivali market. Vegetable waste rotting in the open. Flies everywhere. Market association complaining but no action taken.",
        "image_filename": "garbage_04.jpg",
        "ward": "Ward 9 - Borivali",
    },
    {
        "report_id": "CIV-2026-1036",
        "timestamp": "2026-07-04T13:00:00+05:30",
        "citizen_name": "Pallavi Datar",
        "location": {"latitude": 19.0330, "longitude": 72.8430, "address": "Horniman Circle Area, Fort", "ward": "Ward 2 - Fort"},
        "description": "Drainage problem at Horniman Circle. After every rain, water stays for hours. The heritage structures are getting damaged due to prolonged waterlogging.",
        "image_filename": "drainage_02.jpg",
        "ward": "Ward 2 - Fort",
    },
    {
        "report_id": "CIV-2026-1037",
        "timestamp": "2026-07-01T19:30:00+05:30",
        "citizen_name": "Yogesh Pawar",
        "location": {"latitude": 19.0660, "longitude": 72.8610, "address": "Nana Chowk, Grant Road", "ward": "Ward 4 - Grant Road"},
        "description": "Streetlight pole tilting dangerously at Nana Chowk. Light not working and the pole could fall on parked vehicles or pedestrians.",
        "image_filename": "streetlight_03.jpg",
        "ward": "Ward 4 - Grant Road",
    },
    {
        "report_id": "CIV-2026-1038",
        "timestamp": "2026-07-03T08:00:00+05:30",
        "citizen_name": "Manisha Raut",
        "location": {"latitude": 19.1510, "longitude": 72.8810, "address": "Thane Border Nullah Road", "ward": "Ward 10 - Thane Border"},
        "description": "Sewage overflowing from open nullah near Thane border. The nullah has not been cleaned before monsoon. Unbearable stench in the entire area.",
        "image_filename": "sewage_03.jpg",
        "ward": "Ward 10 - Thane Border",
    },
    {
        "report_id": "CIV-2026-1039",
        "timestamp": "2026-07-02T14:00:00+05:30",
        "citizen_name": "Tushar Joshi",
        "location": {"latitude": 19.1250, "longitude": 72.8520, "address": "JVLR, Andheri East", "ward": "Ward 7 - Andheri East"},
        "description": "Garbage dumped illegally on JVLR service road. Someone is dumping construction waste at night. The pile is growing and blocking half the road.",
        "image_filename": "garbage_05.jpg",
        "ward": "Ward 7 - Andheri East",
    },
    {
        "report_id": "CIV-2026-1040",
        "timestamp": "2026-07-04T07:00:00+05:30",
        "citizen_name": "Leela Hegde",
        "location": {"latitude": 19.1189, "longitude": 72.8471, "address": "Near Chakala Metro Pillar 28, Andheri East", "ward": "Ward 7 - Andheri East"},
        "description": "Water pipe burst near metro pillar 28, Chakala. This looks like the same leak others reported but it is getting much worse now. Water is gushing out at high pressure.",
        "image_filename": "leak_05.jpg",
        "status": "SUBMITTED",
        "ward": "Ward 7 - Andheri East",
        "scenario_id": 1,
    },
    {
        "report_id": "CIV-2026-1041",
        "timestamp": "2026-07-05T10:00:00+05:30",
        "citizen_name": "Ashok Jadhav",
        "location": {"latitude": 19.0450, "longitude": 72.8550, "address": "Prabhadevi Road", "ward": "Ward 5 - Bandra West"},
        "description": "Road damaged on Prabhadevi road near Siddhivinayak temple. The divider is also broken. Heavy traffic area, very risky for pedestrians crossing.",
        "image_filename": "road_damage_05.jpg",
        "ward": "Ward 5 - Bandra West",
    },
    {
        "report_id": "CIV-2026-1042",
        "timestamp": "2026-07-01T15:00:00+05:30",
        "citizen_name": "Nandini Bose",
        "location": {"latitude": 19.0550, "longitude": 72.8450, "address": "Linking Road, Bandra West", "ward": "Ward 5 - Bandra West"},
        "description": "Pothole on Linking Road near the shopping area. Autorickshaws are charging extra to take this route because of road condition. Customers avoiding the market.",
        "image_filename": "pothole_09.jpg",
        "ward": "Ward 5 - Bandra West",
    },
    {
        "report_id": "CIV-2026-1043",
        "timestamp": "2026-07-03T11:00:00+05:30",
        "citizen_name": "Vishal Shetty",
        "location": {"latitude": 19.0750, "longitude": 72.8700, "address": "Charni Road, Marine Lines", "ward": "Ward 3 - Marine Lines"},
        "description": "Small water leak from pipe on Charni Road. Not urgent but wasting water. The area becomes slippery for pedestrians when wet.",
        "image_filename": "leak_06.jpg",
        "ward": "Ward 3 - Marine Lines",
    },
    {
        "report_id": "CIV-2026-1044",
        "timestamp": "2026-07-04T06:30:00+05:30",
        "citizen_name": "Uma Maheshwari",
        "location": {"latitude": 19.0850, "longitude": 72.8550, "address": "Sion-Kurla Road", "ward": "Ward 6 - Kurla"},
        "description": "Garbage overflow at Sion-Kurla road junction. Multiple bins overflowing. Waste scattered by wind and stray animals. Unhygienic for nearby food stalls.",
        "image_filename": "garbage_06.jpg",
        "ward": "Ward 6 - Kurla",
    },
    {
        "report_id": "CIV-2026-1045",
        "timestamp": "2026-07-02T20:30:00+05:30",
        "citizen_name": "Rahul Khare",
        "location": {"latitude": 19.1050, "longitude": 72.8650, "address": "Jogeshwari East", "ward": "Ward 7 - Andheri East"},
        "description": "Streetlight not working on Jogeshwari East main road. Dark stretch of about 200 meters. Recent chain snatching incidents reported in this area.",
        "image_filename": "streetlight_04.jpg",
        "ward": "Ward 7 - Andheri East",
    },
    {
        "report_id": "CIV-2026-1046",
        "timestamp": "2026-07-05T12:00:00+05:30",
        "citizen_name": "Sarita Pardeshi",
        "location": {"latitude": 19.1150, "longitude": 72.8750, "address": "Powai Lake Road", "ward": "Ward 7 - Andheri East"},
        "description": "Drainage issue near Powai Lake. Water from the road is not draining into the lake drainage system. Puddles forming on the jogging track. Lake overflow risk during heavy rain.",
        "image_filename": "drainage_03.jpg",
        "ward": "Ward 7 - Andheri East",
    },
    {
        "report_id": "CIV-2026-1047",
        "timestamp": "2026-07-01T07:00:00+05:30",
        "citizen_name": "Dinesh Solanki",
        "location": {"latitude": 19.0950, "longitude": 72.8450, "address": "Nehru Nagar, Kurla", "ward": "Ward 6 - Kurla"},
        "description": "Sewage overflow at Nehru Nagar Kurla. The old sewage line has burst. Raw sewage flowing on the street. Children play in this area. Major health risk.",
        "image_filename": "sewage_04.jpg",
        "ward": "Ward 6 - Kurla",
    },
    {
        "report_id": "CIV-2026-1048",
        "timestamp": "2026-07-04T16:00:00+05:30",
        "citizen_name": "Madhuri Gokhale",
        "location": {"latitude": 19.0350, "longitude": 72.8400, "address": "Girgaon Chowpatty Road, Fort", "ward": "Ward 2 - Fort"},
        "description": "Exposed wires near Girgaon Chowpatty. Junction box open and wires visible. Beach area with many visitors including children. Risk of electrocution especially during rain.",
        "image_filename": "exposed_wire_04.jpg",
        "ward": "Ward 2 - Fort",
    },
    {
        "report_id": "CIV-2026-1049",
        "timestamp": "2026-07-03T17:00:00+05:30",
        "citizen_name": "Satish Bhagat",
        "location": {"latitude": 19.0480, "longitude": 72.8520, "address": "Mahim Causeway", "ward": "Ward 5 - Bandra West"},
        "description": "Waterlogging on Mahim Causeway. Every time it rains, this stretch floods. Traffic comes to a standstill. The drainage under the causeway seems inadequate.",
        "image_filename": "waterlogging_05.jpg",
        "ward": "Ward 5 - Bandra West",
    },
    {
        "report_id": "CIV-2026-1050",
        "timestamp": "2026-07-05T08:00:00+05:30",
        "citizen_name": "Geeta Mishra",
        "location": {"latitude": 19.1100, "longitude": 72.8600, "address": "Andheri West Station Road", "ward": "Ward 7 - Andheri East"},
        "description": "Drain blocked with plastic waste on Andheri West station road. The drain cover is missing and the open drain is a hazard. Plastic bags visible clogging the flow.",
        "image_filename": "drain_04.jpg",
        "ward": "Ward 7 - Andheri East",
    },
]

# ─── Perception lookup table (deterministic for demo reliability) ────────────

PERCEPTION_LOOKUP = {
    "leak_01.jpg": {"issue_type": "WATER_LEAKAGE", "severity": "HIGH", "confidence": 0.91, "evidence_text": "Visible water accumulation on road surface indicating underground pipe rupture. Continuous water flow pattern suggests pressurized supply line breach. Road surface appears saturated with mineral staining consistent with prolonged water exposure."},
    "leak_02.jpg": {"issue_type": "WATER_LEAKAGE", "severity": "HIGH", "confidence": 0.88, "evidence_text": "Active water seepage from road surface crack. Flow rate and clarity suggest potable water supply line damage. Wet zone extends approximately 5 meters from source point."},
    "leak_03.jpg": {"issue_type": "WATER_LEAKAGE", "severity": "MEDIUM", "confidence": 0.85, "evidence_text": "Minor water seepage near footpath edge. Low flow rate suggests small pipe joint failure. Localized wet patch without significant road damage."},
    "leak_04.jpg": {"issue_type": "WATER_LEAKAGE", "severity": "MEDIUM", "confidence": 0.83, "evidence_text": "Slow water leak from exposed pipe section. Consistent drip pattern indicates joint or valve issue. Limited area of impact."},
    "leak_05.jpg": {"issue_type": "WATER_LEAKAGE", "severity": "CRITICAL", "confidence": 0.94, "evidence_text": "High-pressure water burst from underground main. Significant volume of water flowing onto road. Geyser-like eruption indicates major supply line failure requiring emergency response."},
    "leak_06.jpg": {"issue_type": "WATER_LEAKAGE", "severity": "LOW", "confidence": 0.80, "evidence_text": "Minor dampness on road surface near pipe junction. No active flow visible. Possible slow seep from aging pipe infrastructure."},
    "road_damage_01.jpg": {"issue_type": "ROAD_DAMAGE", "severity": "HIGH", "confidence": 0.89, "evidence_text": "Extensive surface cracking with visible sub-base erosion. Crack pattern consistent with water-induced base failure. Road surface depression indicates undermining by subsurface water flow."},
    "road_damage_02.jpg": {"issue_type": "ROAD_DAMAGE", "severity": "MEDIUM", "confidence": 0.85, "evidence_text": "Surface-level cracking and bitumen peeling on service road. Early-stage deterioration with multiple longitudinal cracks. No base failure visible yet."},
    "road_damage_03.jpg": {"issue_type": "ROAD_DAMAGE", "severity": "MEDIUM", "confidence": 0.84, "evidence_text": "Surface wear and cracking on main road. Bitumen layer showing signs of aging and heavy vehicle stress. Multiple transverse cracks visible."},
    "road_damage_04.jpg": {"issue_type": "ROAD_DAMAGE", "severity": "HIGH", "confidence": 0.87, "evidence_text": "Severe road surface damage with displaced speed breakers. Evidence of heavy vehicle impact on weakened road base. Multiple potholes forming in the damaged stretch."},
    "road_damage_05.jpg": {"issue_type": "ROAD_DAMAGE", "severity": "HIGH", "confidence": 0.86, "evidence_text": "Road surface and divider damage in high-traffic area. Broken curb and displaced median. Signs of repeated heavy vehicle encroachment."},
    "pothole_01.jpg": {"issue_type": "POTHOLE", "severity": "HIGH", "confidence": 0.93, "evidence_text": "Deep pothole approximately 60cm diameter and 30cm depth. Filled with standing muddy water. Edges showing further erosion. Located in active traffic lane with no warning markers."},
    "pothole_02.jpg": {"issue_type": "POTHOLE", "severity": "MEDIUM", "confidence": 0.87, "evidence_text": "Medium-sized pothole near traffic signal. Approximately 40cm wide. Position at turning point increases collision risk for two-wheelers."},
    "pothole_03.jpg": {"issue_type": "POTHOLE", "severity": "HIGH", "confidence": 0.90, "evidence_text": "Previously reported pothole has enlarged. Depth increased significantly. Fresh edge breakage visible indicating ongoing deterioration. Active safety hazard."},
    "pothole_04.jpg": {"issue_type": "POTHOLE", "severity": "HIGH", "confidence": 0.92, "evidence_text": "Pothole at previously repaired location. Patch material has dislodged completely. Underlying base failure visible. Repair quality was inadequate for traffic load."},
    "pothole_05.jpg": {"issue_type": "ROAD_DAMAGE", "severity": "HIGH", "confidence": 0.88, "evidence_text": "Extended road damage around failed pothole repair site. Surface breaking apart in 20-meter stretch. Base layer exposed. Complete resurfacing required."},
    "pothole_06.jpg": {"issue_type": "POTHOLE", "severity": "LOW", "confidence": 0.82, "evidence_text": "Small pothole at road turning. Shallow depth but positioned to catch drivers off-guard. Minor surface-level damage."},
    "pothole_07.jpg": {"issue_type": "POTHOLE", "severity": "MEDIUM", "confidence": 0.86, "evidence_text": "Medium pothole near railway crossing. Uneven road surface around it. Position forces vehicles to slow down creating bottleneck."},
    "pothole_08.jpg": {"issue_type": "POTHOLE", "severity": "HIGH", "confidence": 0.89, "evidence_text": "Multiple potholes on service road stretch. At least 5 visible in frame. Road surface severely degraded. Systematic failure rather than isolated damage."},
    "pothole_09.jpg": {"issue_type": "POTHOLE", "severity": "MEDIUM", "confidence": 0.84, "evidence_text": "Pothole in commercial area road. Moderate depth. Located near shops causing access difficulties for customers and delivery vehicles."},
    "waterlogging_01.jpg": {"issue_type": "WATERLOGGING", "severity": "HIGH", "confidence": 0.90, "evidence_text": "Significant standing water on road surface, approximately ankle-deep. Visible debris floating. No drainage visible. Road damage and potholes acting as water retention basins."},
    "waterlogging_02.jpg": {"issue_type": "WATERLOGGING", "severity": "MEDIUM", "confidence": 0.85, "evidence_text": "Moderate waterlogging in market area. Water level reaching shop entrances. Blocked drain visible as contributing factor. Stagnant water with debris."},
    "waterlogging_03.jpg": {"issue_type": "WATERLOGGING", "severity": "HIGH", "confidence": 0.88, "evidence_text": "Severe stagnant water with visible algae growth indicating multi-day accumulation. Green discoloration suggests health hazard. Mosquito breeding conditions present."},
    "waterlogging_04.jpg": {"issue_type": "WATERLOGGING", "severity": "HIGH", "confidence": 0.87, "evidence_text": "Extensive waterlogging at bus depot approach. Water depth preventing vehicle entry. Large surface area affected. Drainage infrastructure overwhelmed."},
    "waterlogging_05.jpg": {"issue_type": "WATERLOGGING", "severity": "MEDIUM", "confidence": 0.83, "evidence_text": "Recurring waterlogging on causeway. Low-lying area with inadequate drainage capacity. Water accumulation pattern suggests structural drainage deficiency."},
    "drain_01.jpg": {"issue_type": "DRAIN_BLOCKAGE", "severity": "HIGH", "confidence": 0.88, "evidence_text": "Drain mouth completely blocked with plastic waste and construction debris. No water flow visible. Surrounding area shows water accumulation from blocked outflow."},
    "drain_02.jpg": {"issue_type": "DRAIN_BLOCKAGE", "severity": "MEDIUM", "confidence": 0.84, "evidence_text": "Partially blocked drain near bus stop. Floating debris reducing flow capacity. Water backing up at drain inlet. Secondary blockage developing."},
    "drain_03.jpg": {"issue_type": "DRAIN_BLOCKAGE", "severity": "MEDIUM", "confidence": 0.82, "evidence_text": "Drain blocked with construction debris in residential area. Cement and brick fragments visible in drain. Water level rising above normal."},
    "drain_04.jpg": {"issue_type": "DRAIN_BLOCKAGE", "severity": "MEDIUM", "confidence": 0.81, "evidence_text": "Open drain with plastic waste blockage. Missing drain cover creating pedestrian hazard. Plastic bags clogging water flow."},
    "garbage_01.jpg": {"issue_type": "GARBAGE_OVERFLOW", "severity": "MEDIUM", "confidence": 0.86, "evidence_text": "Overflowing garbage collection point. Mixed waste including organic and plastic. Waste mixing with waterlogged area creating contamination. Stray animals scavenging."},
    "garbage_02.jpg": {"issue_type": "GARBAGE_OVERFLOW", "severity": "MEDIUM", "confidence": 0.84, "evidence_text": "Multiple bins overflowing in market area. Waste bags torn by animals. Scattered waste on road surface. Collection schedule appears inadequate."},
    "garbage_03.jpg": {"issue_type": "GARBAGE_OVERFLOW", "severity": "MEDIUM", "confidence": 0.83, "evidence_text": "Community bin overflow. Waste piled above bin capacity. Organic waste decomposing. Flies and insects visible. Residential area affected."},
    "garbage_04.jpg": {"issue_type": "GARBAGE_OVERFLOW", "severity": "HIGH", "confidence": 0.85, "evidence_text": "Market area garbage overflow with vegetable waste. Rotting organic matter creating health hazard. Area near food stalls, food safety risk."},
    "garbage_05.jpg": {"issue_type": "GARBAGE_OVERFLOW", "severity": "HIGH", "confidence": 0.87, "evidence_text": "Illegal construction waste dumping on service road. Large pile of debris including concrete and metal. Road partially blocked. Night dumping suspected."},
    "garbage_06.jpg": {"issue_type": "GARBAGE_OVERFLOW", "severity": "MEDIUM", "confidence": 0.82, "evidence_text": "Overflowing bins at road junction. Wind-scattered waste across road. Multiple bins full, collection overdue. Traffic area needs priority cleanup."},
    "exposed_wire_01.jpg": {"issue_type": "EXPOSED_WIRES", "severity": "CRITICAL", "confidence": 0.94, "evidence_text": "Exposed high-voltage wires hanging from damaged pole near school entrance. Insulation completely stripped. Wire at approximately 1.5m height — within reach of children. Immediate electrocution risk, amplified during rain."},
    "exposed_wire_02.jpg": {"issue_type": "EXPOSED_WIRES", "severity": "CRITICAL", "confidence": 0.92, "evidence_text": "Broken streetlight with exposed internal wiring on school path. Junction box damaged and open. Multiple bare copper conductors visible. Combination with wet monsoon conditions creates lethal hazard."},
    "exposed_wire_03.jpg": {"issue_type": "EXPOSED_WIRES", "severity": "HIGH", "confidence": 0.89, "evidence_text": "Exposed wires from melted insulation in industrial area. Overload damage visible on conductors. Warning sign placed by locals but wire remains energized."},
    "exposed_wire_04.jpg": {"issue_type": "EXPOSED_WIRES", "severity": "HIGH", "confidence": 0.88, "evidence_text": "Open junction box with exposed wires near beach area. Box cover missing. Internal connections visible and accessible. High foot traffic area with children."},
    "streetlight_01.jpg": {"issue_type": "BROKEN_STREETLIGHT", "severity": "MEDIUM", "confidence": 0.87, "evidence_text": "Non-functional streetlight on main road. Lamp housing intact but no illumination. Likely electrical supply or bulb failure. Dark stretch creates safety concern."},
    "streetlight_02.jpg": {"issue_type": "BROKEN_STREETLIGHT", "severity": "MEDIUM", "confidence": 0.85, "evidence_text": "Multiple non-functional streetlights on station road. Three consecutive lights out creating extended dark zone. Possible common electrical supply issue."},
    "streetlight_03.jpg": {"issue_type": "BROKEN_STREETLIGHT", "severity": "HIGH", "confidence": 0.88, "evidence_text": "Tilting streetlight pole at intersection. Base mount appears corroded. Pole leaning at approximately 15 degrees. Risk of collapse onto parked vehicles or pedestrians."},
    "streetlight_04.jpg": {"issue_type": "BROKEN_STREETLIGHT", "severity": "MEDIUM", "confidence": 0.84, "evidence_text": "Streetlight out on main road stretch. Area known for safety issues. Dark zone approximately 200 meters. Street lighting is sole illumination source."},
    "sewage_01.jpg": {"issue_type": "SEWAGE_OVERFLOW", "severity": "HIGH", "confidence": 0.89, "evidence_text": "Sewage overflowing from manhole. Dark contaminated water spreading on heritage road. Manhole cover partially displaced. Sewage line pressure buildup indicated."},
    "sewage_02.jpg": {"issue_type": "SEWAGE_OVERFLOW", "severity": "HIGH", "confidence": 0.87, "evidence_text": "Sewage from dislodged manhole near nullah. Contaminated water mixing with road drainage. Vehicles splashing sewage onto pedestrians. Health and hygiene hazard."},
    "sewage_03.jpg": {"issue_type": "SEWAGE_OVERFLOW", "severity": "HIGH", "confidence": 0.86, "evidence_text": "Open nullah overflow with raw sewage. Pre-monsoon cleaning not completed. Accumulated waste in nullah causing overflow. Wide area stench impact."},
    "sewage_04.jpg": {"issue_type": "SEWAGE_OVERFLOW", "severity": "CRITICAL", "confidence": 0.91, "evidence_text": "Burst sewage line in residential area. Raw sewage flowing on street. Children's play area affected. Major public health emergency requiring immediate response."},
    "drainage_01.jpg": {"issue_type": "DRAINAGE_PROBLEM", "severity": "MEDIUM", "confidence": 0.83, "evidence_text": "Inadequate drainage grating on main road. Water ponding hours after rain stopped. Grating size insufficient for water volume. Structural drainage capacity issue."},
    "drainage_02.jpg": {"issue_type": "DRAINAGE_PROBLEM", "severity": "MEDIUM", "confidence": 0.81, "evidence_text": "Chronic drainage problem in heritage area. Repeated water retention after rainfall. Drainage infrastructure appears inadequate for current surface area."},
    "drainage_03.jpg": {"issue_type": "DRAINAGE_PROBLEM", "severity": "MEDIUM", "confidence": 0.82, "evidence_text": "Drainage capacity issue near lake. Jogging track affected by standing water. Overflow risk during heavy rain events. Storm drain connection appears insufficient."},
    # Verification images (for demo resolution workflow)
    "resolved_leak_correct.jpg": {"issue_type": "WATER_LEAKAGE", "severity": "LOW", "confidence": 0.95, "evidence_text": "Road surface appears dry. New pipe joint visible indicating completed repair. No water seepage detected. Area cleaned and restored."},
    "resolved_leak_wrong.jpg": {"issue_type": "GARBAGE_OVERFLOW", "severity": "MEDIUM", "confidence": 0.78, "evidence_text": "Image shows a different location — garbage collection area. No water infrastructure visible. Does not match the incident location for water leakage verification."},
}


def generate_reports():
    """Generate all 50 reports deterministically."""
    all_reports = []

    # Add scenario reports
    for report in SCENARIO_1_REPORTS:
        all_reports.append(report)

    for report in SCENARIO_2_REPORTS:
        all_reports.append(report)

    for report in SCENARIO_3_REPORTS:
        all_reports.append(report)

    for report in SCENARIO_4_REPORTS:
        all_reports.append(report)

    # Add independent reports (fill in default fields)
    for i, report in enumerate(INDEPENDENT_REPORTS):
        if "status" not in report:
            report["status"] = "SUBMITTED"
        if "phone" not in report:
            report["phone"] = f"+91-98200-{10018 + i:05d}"
        if "scenario_id" not in report:
            report["scenario_id"] = None
        if "linked_incident_id" not in report:
            report["linked_incident_id"] = None
        all_reports.append(report)

    # Ensure all reports have linked_incident_id
    for report in all_reports:
        if "linked_incident_id" not in report:
            report["linked_incident_id"] = None

    return all_reports


def generate_seed_data():
    """Generate all seed data files."""
    ensure_data_dir()

    # Generate complaints
    reports = generate_reports()
    complaints_path = os.path.join(DATA_DIR, "complaints.json")
    with open(complaints_path, "w", encoding="utf-8") as f:
        json.dump({"reports": reports, "total": len(reports)}, f, indent=2, ensure_ascii=False)
    print(f"[OK] Generated {len(reports)} reports -> {complaints_path}")

    # Empty incidents
    incidents_path = os.path.join(DATA_DIR, "incidents.json")
    with open(incidents_path, "w", encoding="utf-8") as f:
        json.dump({"incidents": [], "total": 0}, f, indent=2)
    print(f"[OK] Generated empty incidents -> {incidents_path}")

    # Empty agent logs
    logs_path = os.path.join(DATA_DIR, "agent_logs.json")
    with open(logs_path, "w", encoding="utf-8") as f:
        json.dump({"logs": [], "total": 0}, f, indent=2)
    print(f"[OK] Generated empty agent logs -> {logs_path}")

    # Save perception lookup (agents read this)
    lookup_path = os.path.join(DATA_DIR, "perception_lookup.json")
    with open(lookup_path, "w", encoding="utf-8") as f:
        json.dump(PERCEPTION_LOOKUP, f, indent=2, ensure_ascii=False)
    print(f"[OK] Generated perception lookup -> {lookup_path}")

    # Scenario metadata
    scenarios = {
        "scenarios": [
            {
                "scenario_id": 1,
                "title": "Water Infrastructure Cascade",
                "description": "Water leakage → road damage → pothole → waterlogging. Main demo scenario showing how a single pipe leak causes cascading infrastructure failure.",
                "ward": "Ward 7 - Andheri East",
                "report_ids": [r["report_id"] for r in SCENARIO_1_REPORTS] + ["CIV-2026-1040"],
                "expected_incident_id": "INC-2026-001",
                "expected_chain": ["WATER_LEAKAGE", "ROAD_DAMAGE", "POTHOLE", "WATERLOGGING"],
                "expected_impact_score": 86,
                "expected_priority": "CRITICAL",
            },
            {
                "scenario_id": 2,
                "title": "Drainage-Waste Cycle",
                "description": "Drain blockage → waterlogging → garbage accumulation. Shows how blocked drains create a self-reinforcing cycle of flooding and waste buildup.",
                "ward": "Ward 6 - Kurla",
                "report_ids": [r["report_id"] for r in SCENARIO_2_REPORTS],
                "expected_incident_id": "INC-2026-002",
                "expected_chain": ["DRAIN_BLOCKAGE", "WATERLOGGING", "GARBAGE_OVERFLOW"],
                "expected_impact_score": 72,
                "expected_priority": "HIGH",
            },
            {
                "scenario_id": 3,
                "title": "Electrical Safety Hazard Near School",
                "description": "Exposed electrical wires near a school. Only 2 reports but CRITICAL impact — proves that priority ≠ complaint count.",
                "ward": "Ward 3 - Marine Lines",
                "report_ids": [r["report_id"] for r in SCENARIO_3_REPORTS],
                "expected_incident_id": "INC-2026-003",
                "expected_chain": ["BROKEN_STREETLIGHT", "EXPOSED_WIRES"],
                "expected_impact_score": 91,
                "expected_priority": "CRITICAL",
            },
            {
                "scenario_id": 4,
                "title": "Recurring Pothole Failure",
                "description": "Repeated pothole reports after a claimed resolution. Proves the verification and reopen logic — resolution failed, incident must reopen.",
                "ward": "Ward 5 - Bandra West",
                "report_ids": [r["report_id"] for r in SCENARIO_4_REPORTS],
                "expected_incident_id": "INC-2026-004",
                "expected_chain": ["POTHOLE", "ROAD_DAMAGE"],
                "expected_impact_score": 68,
                "expected_priority": "HIGH",
            },
        ]
    }
    scenarios_path = os.path.join(DATA_DIR, "scenarios.json")
    with open(scenarios_path, "w", encoding="utf-8") as f:
        json.dump(scenarios, f, indent=2, ensure_ascii=False)
    print(f"[OK] Generated scenario metadata -> {scenarios_path}")

    print(f"\n=== Seed data generation complete. {len(reports)} reports across 4 scenarios. ===")
    return reports


if __name__ == "__main__":
    generate_seed_data()
