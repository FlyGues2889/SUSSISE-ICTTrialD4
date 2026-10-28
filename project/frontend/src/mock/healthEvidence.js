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
}