"""
Angle rules for exercise form & range of motion
Angles are in degrees
Tolerance means acceptable deviation
min/max are used for rep counting
"""

EXERCISE_RULES = {

    "barbell biceps curl": {
        "elbow": {
            "min": 30,      # أقل زاوية (انكماش كامل)
            "max": 160      # أكبر زاوية (انبساط كامل)
        },
        "hip": {
            "target": 170,
            "tolerance": 20
        }
    },

    "hammer curl": {
        "elbow": {
            "min": 30,      # زي الـ barbell curl
            "max": 160
        },
        "hip": {
            "target": 170,
            "tolerance": 20
        }
    },

    "bench press": {
        # 🔄 Using SHOULDER instead of ELBOW because side-camera views cause elbow foreshortening
        "shoulder": {
            "min": 35,      # Form Check: arm position at bar-down (acceptable: 35-65°)
            "max": 65,      # Form Check: arm position at bar-up
            "rep_start": 58, # Made easier: Trigger START when angle ≤ 58 (less depth required)
            "rep_end": 60    # Trigger END when angle ≥ 60 (bar coming up)
        },
        "elbow": {
            "target": 160,  # Form Check only: arms should be relatively straight at lockout
            "tolerance": 30
        },
        "hip": {
            "target": 170,
            "tolerance": 40  # Relaxed for lying position
        }
    },

    "incline bench press": {
        "elbow": {
            "min": 50,
            "max": 160
        },
        "hip": {
            "target": 170,
            "tolerance": 20
        }
    },

    "decline bench press": {
        "elbow": {
            "min": 50,
            "max": 160
        },
        "hip": {
            "target": 170,
            "tolerance": 20
        }
    },

    "chest fly machine": {
        "shoulder": {
            "min": 30,      # threshold = 45 (angles ≤45 = START)
            "max": 65       # threshold = 50 (angles ≥50 = END)
        },
        "elbow": {
            "target": 140,
            "tolerance": 40
        }
    },

    "shoulder press": {
        "elbow": {
            "min": 20,      # Form Check: Allow deep reps down to 20 degrees
            "max": 175,     # Form Check: Allow full lockout (was 155, caused errors at 161)
            "rep_start": 80,  # Rep Count: Trigger START when angle ≤ 80
            "rep_end": 145    # Rep Count: Trigger END when angle ≥ 145
        },
        "shoulder": {
            "min": 70,
            "max": 160
        },
        "hip": {
            "target": 170,
            "tolerance": 20
        }
    },

    "lateral raises": {
        "shoulder": {
            "min": 15,      # ذراع جنب الجسم
            "max": 85       # ذراع مرفوعة
        },
        "hip": {
            "target": 170,
            "tolerance": 20
        }
    },

    "lat pulldown": {
        "elbow": {
            "min": 40,      # سحب كامل (Allow deep pull)
            "max": 175,     # ذراع ممتدة (Relaxed max to allow 169-170 without error)
            "rep_start": 110, # Trigger START (down) when angle <= 110 (User hitting 96-99, so 110 is safe)
            "rep_end": 145   # Trigger END (up) when angle >= 145
        },
        "hip": {
            "target": 90,
            "tolerance": 50  # Relax form check (allow 40-140 deg) to accept leaning back/forward
        }
    },

    "pull up": {        ## done ##
        "elbow": {
            "min": 50,      # سحب كامل
            "max": 160      # ذراع ممتدة
        }
    },

    "t bar row": {
        "elbow": {
            "min": 115,     # سحب كامل - threshold = 130 (angles ≤130 = START)
            "max": 155      # ذراع ممتدة - threshold = 140 (angles ≥140 = END)
        },
        "hip": {
            "target": 100,
            "tolerance": 40
        }
    },

    "tricep dips": {
        "elbow": {
            "min": 60,      # كان 100 - ده ضيق جداً
            "max": 160
        },
        "hip": {
            "target": 170,
            "tolerance": 20
        }
    },

    "tricep pushdown": {
        "elbow": {
            "min": 90,      # threshold = 105 (angles ≤105 = START)
            "max": 160      # threshold = 145 (angles ≥145 = END)
        },
        "hip": {
            "target": 160,
            "tolerance": 20
        }
    },

    "push up": {
        "elbow": {
            "min": 60,      # كان 80 - محتاج يكون أقل
            "max": 160
        },
        "hip": {
            "target": 170,
            "tolerance": 15
        }
    },

    "plank": {
        # الـ plank مفيهوش عد - بس بنتتبع الـ form
        "hip": {
            "target": 170,
            "tolerance": 10
        }
    },

    "squat": {
        "knee": {
            "min": 60,      # كان 20 - ده صعب جداً
            "max": 160
        },
        "hip": {
            "min": 50,
            "max": 160
        }
    },

    "deadlift": {
        "hip": {
            "min": 100,     # الجسم منحني - threshold سيكون 115
            "max": 155      # الجسم مفرود - threshold سيكون 140
        },
        "knee": {
            "target": 160,
            "tolerance": 25
        }
    },

    "romanian deadlift": {
        "hip": {
            "min": 70,      # كان 80
            "max": 160
        },
        "knee": {
            "min": 140,
            "max": 175
        }
    },

    "hip thrust": {
        "hip": {
            "min": 80,      # كان 100
            "max": 170      # كان 160
        },
        "knee": {
            "target": 90,
            "tolerance": 25
        }
    },

    "leg extension": {
        "knee": {
            "min": 105,     # threshold = 120 (angles ≤120 = START)
            "max": 125      # threshold = 110 (angles ≥110 = END) - أوسع للفيديوهات المختلفة
        },
        "hip": {
            "target": 90,
            "tolerance": 20
        }
    },

    "leg raises": {
        "hip": {
            "min": 80,      # threshold = 95
            "max": 150      # threshold = 135 (كان 140 - بيفوت عدات)
        }
    },

    "russian twist": {
        "shoulder": {
            "min": 0,       # threshold = 15 (angles ≤15 = START)
            "max": 37       # threshold = 22 (angles ≥22 = END) - لالتقاط اللفات الضعيفة (جانب الكاميرا)
        },
        "hip": {
            "target": 120,
            "tolerance": 20
        }
    }
}
