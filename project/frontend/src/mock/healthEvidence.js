export const healthEvidence = {
  sources: [
    {
      id: 'who_physical_activity',
      title: 'WHO身体活动实况报道',
      date: '2024-06-26',
      url: 'https://www.who.int/zh/news-room/fact-sheets/detail/physical-activity',
      publisher: '世界卫生组织（WHO）',
    },
    {
      id: 'who_musculoskeletal',
      title: 'WHO肌肉骨骼疾病实况报道',
      date: '2021-02-08',
      url: 'https://www.who.int/zh/news-room/fact-sheets/detail/musculoskeletal-conditions',
      publisher: '世界卫生组织（WHO）',
    },
    {
      id: 'who_guidelines_pdf',
      title: '世卫组织关于身体活动和久坐行为的指南',
      date: '2020',
      url: 'https://iris.who.int/bitstream/handle/10665/336656/9789240032156-chi.pdf',
      publisher: '世界卫生组织（WHO）',
    },
    {
      id: 'nhs_back_pain',
      title: 'Back pain',
      date: '2024',
      url: 'https://www.nhs.uk/conditions/back-pain/',
      publisher: '英国国家医疗服务体系（NHS）',
    },
    {
      id: 'csp_neck_pain',
      title: 'Treatment for neck pain',
      date: '2024',
      url: 'https://www.csp.org.uk/conditions/neck-pain/treatment-neck-pain',
      publisher: '英国特许物理治疗学会（CSP）',
    },
    {
      id: 'csep_24h',
      title: 'Canadian 24-Hour Movement Guidelines (18–64 years)',
      date: '2021',
      url: 'https://csepguidelines.ca/guidelines/adults-18-64/',
      publisher: '加拿大运动生理学会（CSEP）',
    },
    {
      id: 'hhs_pag',
      title: 'Physical Activity Guidelines for Americans, 2nd edition',
      date: '2018',
      url: 'https://odphp.health.gov/our-work/nutrition-physical-activity/physical-activity-guidelines/current-guidelines',
      publisher: '美国卫生与公众服务部（HHS）',
    },
  ],

  sedentaryBehavior: {
    definition: '久坐行为是指在清醒期间的任何低能量消耗期间，如坐、斜躺或躺。',
    risks: [
      '久坐行为增加全因死亡率、心血管疾病和癌症的死亡率',
      '久坐行为增加心血管疾病、癌症和2型糖尿病的发病率',
      '身体活动不足者的死亡风险增加20%至30%',
    ],
    recommendation: '任何数量的身体活动都比没有好；所有年龄组都应限制久坐的时间。',
    sourceId: 'who_physical_activity',
  },

  musculoskeletal: {
    neckPain: {
      prevalence: '全球颈部疼痛影响2.22亿人',
      impact: '肌肉骨骼疾病是全球残疾的主要原因，在160个国家中腰痛是造成残疾的最主要原因',
      sourceId: 'who_musculoskeletal',
    },
    backPain: {
      prevalence: '全球腰痛影响5.68亿人，是肌肉骨骼疾病中负担最重的',
      impact: '腰痛是过早退出职场的主要原因，与精神健康显著恶化和身体功能下降高度相关',
      sourceId: 'who_musculoskeletal',
    },
    totalPrevalence: '全球约17.1亿人患有肌肉骨骼疾病',
  },

  physicalActivity: {
    adultRecommendation: '成年人每周至少150分钟中等强度身体活动',
    globalStats: '31%的成年人和80%的青少年没有达到建议的身体活动水平',
    benefit: '定期的身体活动有助于预防和管理心血管疾病、癌症和糖尿病等非传染性疾病，并减少抑郁和焦虑症状',
    sourceId: 'who_physical_activity',
  },

  guidelines: [
    {
      id: 'who_any_amount',
      publisher: '世界卫生组织（WHO）',
      abbr: 'WHO',
      region: '全球',
      title: '身体活动实况报道',
      year: '2024',
      url: 'https://www.who.int/zh/news-room/fact-sheets/detail/physical-activity',
      areas: ['full', 'neck', 'back', 'sitting'],
      excerpt: '任何数量的身体活动都比没有好，任何身体活动都有益；所有年龄组都应限制久坐的时间；强健肌肉对每个人都有好处。',
      original: 'Any amount of physical activity is better than none, and all physical activity is beneficial.',
    },
    {
      id: 'who_adult_dose',
      publisher: '世界卫生组织（WHO）',
      abbr: 'WHO',
      region: '全球',
      title: '成年人身体活动建议',
      year: '2024',
      url: 'https://www.who.int/zh/news-room/fact-sheets/detail/physical-activity',
      areas: ['full'],
      excerpt: '成年人每周应进行至少150至300分钟中等强度有氧身体活动，或等量的高强度活动。',
    },
    {
      id: 'who_replace_sitting',
      publisher: '世界卫生组织（WHO）',
      abbr: 'WHO',
      region: '全球',
      title: '身体活动和久坐行为指南',
      year: '2020',
      url: 'https://iris.who.int/bitstream/handle/10665/336656/9789240032156-chi.pdf',
      areas: ['sitting', 'neck', 'back'],
      excerpt: '用任何强度的身体活动替代久坐时间都能带来健康收益，久坐时间越长，健康风险越高。',
    },
    {
      id: 'csep_sedentary',
      publisher: '加拿大运动生理学会（CSEP）',
      abbr: 'CSEP',
      region: '加拿大',
      title: '24小时运动指南（18至64岁）',
      year: '2021',
      url: 'https://csepguidelines.ca/guidelines/adults-18-64/',
      areas: ['sitting', 'back', 'full'],
      excerpt: '每天久坐时间控制在8小时以内，娱乐性屏幕时间不超过3小时，并尽可能频繁地打断长时间坐着。',
      original: 'Limit sedentary time to 8 hours or less. Breaking up long periods of sitting as often as possible.',
    },
    {
      id: 'csep_strength',
      publisher: '加拿大运动生理学会（CSEP）',
      abbr: 'CSEP',
      region: '加拿大',
      title: '24小时运动指南（18至64岁）',
      year: '2021',
      url: 'https://csepguidelines.ca/guidelines/adults-18-64/',
      areas: ['full', 'back', 'neck'],
      excerpt: '每周进行至少150分钟中等至高强度身体活动，并每周至少2次力量训练；轻强度活动如站立也有价值。',
    },
    {
      id: 'nhs_stay_active',
      publisher: '英国国家医疗服务体系（NHS）',
      abbr: 'NHS',
      region: '英国',
      title: '背痛（Back pain）',
      year: '2024',
      url: 'https://www.nhs.uk/conditions/back-pain/',
      areas: ['back'],
      excerpt: '背痛时保持活动，尽量继续日常活动；不要长时间卧床；散步、游泳、瑜伽和普拉提可能有所帮助。',
      original: 'Stay active and try to continue with your daily activities. Do not stay in bed for long periods of time.',
    },
    {
      id: 'nhs_red_flags',
      publisher: '英国国家医疗服务体系（NHS）',
      abbr: 'NHS',
      region: '英国',
      title: '背痛的就医信号',
      year: '2024',
      url: 'https://www.nhs.uk/conditions/back-pain/',
      areas: ['back'],
      kind: 'safety',
      excerpt: '如果出现双腿疼痛、麻木或无力，会阴部感觉丧失，或大小便功能改变，请立即前往急诊就医。',
    },
    {
      id: 'csp_neck_exercise',
      publisher: '英国特许物理治疗学会（CSP）',
      abbr: 'CSP',
      region: '英国',
      title: '颈部疼痛的治疗',
      year: '2024',
      url: 'https://www.csp.org.uk/conditions/neck-pain/treatment-neck-pain',
      areas: ['neck'],
      excerpt: '运动已被证明是治疗持续性颈部疼痛最有帮助的方法；在疼痛允许的范围内尽可能保持活动，大多数颈部疼痛会在3个月内明显好转。',
      original: 'Exercise has been shown to be the most helpful treatment for on-going neck pain.',
    },
    {
      id: 'hhs_adult_dose',
      publisher: '美国卫生与公众服务部（HHS）',
      abbr: 'HHS',
      region: '美国',
      title: '美国人身体活动指南（第2版）',
      year: '2018',
      url: 'https://odphp.health.gov/our-work/nutrition-physical-activity/physical-activity-guidelines/current-guidelines',
      areas: ['full', 'neck', 'back'],
      excerpt: '成年人每周应进行至少150分钟中等强度有氧运动，并每周至少2天进行中等或更高强度的肌肉力量训练。',
    },
  ],

  getEvidenceText(area) {
    if (area === 'neck') {
      return {
        fact: '据WHO数据，全球颈部疼痛影响2.22亿人。肌肉骨骼疾病是全球残疾的主要原因。',
        recommendation: 'WHO建议：任何数量的身体活动都比没有好，所有年龄组都应限制久坐的时间。',
        source: 'WHO肌肉骨骼疾病实况报道（2021）',
        sourceUrl: 'https://www.who.int/zh/news-room/fact-sheets/detail/musculoskeletal-conditions',
      }
    }
    if (area === 'back') {
      return {
        fact: '据WHO数据，全球腰痛影响5.68亿人，是肌肉骨骼疾病中负担最重的。腰痛是过早退出职场的主要原因。',
        recommendation: 'WHO建议：任何数量的身体活动都比没有好，所有年龄组都应限制久坐的时间。',
        source: 'WHO肌肉骨骼疾病实况报道（2021）',
        sourceUrl: 'https://www.who.int/zh/news-room/fact-sheets/detail/musculoskeletal-conditions',
      }
    }
    return {
      fact: '据WHO数据，全球约17.1亿人患有肌肉骨骼疾病。身体活动不足者的死亡风险增加20%至30%。',
      recommendation: 'WHO建议：成年人每周至少150分钟中等强度身体活动。任何数量的身体活动都比没有好。',
      source: 'WHO身体活动实况报道（2024）',
      sourceUrl: 'https://www.who.int/zh/news-room/fact-sheets/detail/physical-activity',
    }
  },

  getPlanEvidence(area) {
    const base = {
      neck: {
        fact: 'WHO数据显示全球颈部疼痛影响2.22亿人，久坐是主要风险因素之一。',
        source: 'WHO肌肉骨骼疾病实况报道',
        sourceUrl: 'https://www.who.int/zh/news-room/fact-sheets/detail/musculoskeletal-conditions',
      },
      back: {
        fact: 'WHO数据显示全球腰痛影响5.68亿人，是肌肉骨骼疾病中负担最重的。',
        source: 'WHO肌肉骨骼疾病实况报道',
        sourceUrl: 'https://www.who.int/zh/news-room/fact-sheets/detail/musculoskeletal-conditions',
      },
      full: {
        fact: 'WHO建议任何数量的身体活动都比没有好，所有年龄组都应限制久坐的时间。',
        source: 'WHO身体活动实况报道',
        sourceUrl: 'https://www.who.int/zh/news-room/fact-sheets/detail/physical-activity',
      },
    }
    return base[area] || base.full
  },

  getGuidelines(area, limit = 2) {
    const key = ['neck', 'back', 'full', 'sitting'].includes(area) ? area : 'full'
    const pool = this.guidelines
      .filter((g) => g.kind !== 'safety' && g.areas.includes(key))
      .sort((a, b) => a.areas.length - b.areas.length)
    const out = []
    const seen = new Set()
    for (const g of pool) {
      if (seen.has(g.abbr)) continue
      seen.add(g.abbr)
      out.push(g)
      if (out.length >= limit) break
    }
    return out
  },

  getPlanGuideline(area) {
    const key = ['neck', 'back', 'full', 'sitting'].includes(area) ? area : 'full'
    return (
      this.guidelines
        .filter((g) => g.kind !== 'safety' && g.abbr !== 'WHO' && g.areas.includes(key))
        .sort((a, b) => a.areas.length - b.areas.length)[0] || null
    )
  },

  getSafetyGuidelines(area) {
    return this.guidelines.filter((g) => g.kind === 'safety' && g.areas.includes(area))
  },

  getGuidelinesByArea(area) {
    return this.guidelines.filter((g) => g.areas.includes(area))
  },
}