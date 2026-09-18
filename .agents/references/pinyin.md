# 拼音

本仓库中，用于数据表示以及内部处理的拼音，有以下几种：

1. ASCII 白话字（ASCII PUJ）：辞典内部数据的存储、口音转换、拼音方案转换都基于此方案。这套方案中不存在 ASCII 码以外的字符，方便录入和口音和其他变换处理。
   例：潮汕方言拼音方案书写，写作 tionn'5-suann1 huang1-ngan5 pheng1-im1 huang1-uann3 tsur1-sia2。
2. 书面白话字（Written PUJ）：辞典最终展示给用户的写法，包含比较难以输入的韵母“ṳ”“o̤”以及白话字声调调符。
   例：潮汕方言拼音方案书写，写作 tiônn'-suann huang-ngân pheng-im huang-uànn tsṳ-siá。
3. 潮拼（DP）：一套经典的也是最流行的潮汕方言拼音方案。
   例：潮汕方言拼音方案书写，写作 dion'5-suan1 huang1-ngand5 pêng1-im1 huang1-uan3 ze1-sia2。
4. X-SAMPA 式国际音标（X-SAMPA IPA）：一种便于键盘输入的国际音标方案，所有字符都在 ASCII 码表范围内。
   本项目中，拓展了几个符号用于标注声调，具体的，数字 1~8 之前分别加上两个下划线，表示相应的声调，例如 __1 表示 1 声，__2 表示 2 声。
   例：潮汕方言拼音方案书写，写作 ti~o~__5-su~a~__1 huaN__1-Nan__5 p_heN__1-im__1 huaN__1-u~a~__3 tsM__1-sia__2。
   如果用户指定了声调使用某一种实际调值，那么将输出实际调值。
   本项目中，使用 _B _L _M _H _T 分别表示五度标记法的 1 2 3 4 5 即 ˩ ˨ ˧ ˦ ˥，加入反斜杠则表示变调，使用 _B\ _L\ _M\ _H\ _T\ 表示变调的 1 2 3 4 5 即 ꜖ ꜕ ꜔ ꜓ ꜒。
   例：潮汕方言拼音方案书写，指定声调为澄海口音，则写作 ti~o~_L\_B\_L\-su~a~_M_M huaN_L\_M\-Nan_T_T p_heN_L\_M\-im_M_M huaN_L\_M\-u~a~_L_B_L tsM_L\_M\-sia_T_L。
5. 国际音标（IPA）：标准国际音标，包含键盘难以录入的复杂字符。
   例：潮汕方言拼音方案书写，写作 tĩõ⁵-sũã¹ huaŋ¹-ŋan⁵ pʰeŋ¹-im¹ huaŋ¹-ũã³ tsɯ¹-sia²。
   如果用户指定了声调使用某一种实际调值，那么将输出实际调值。
   例：潮汕方言拼音方案书写，指定声调为澄海口音，则写作 tĩõ꜕꜖꜕-sũã˧˧ huaŋ꜕꜔-ŋan˥˥ pʰeŋ꜕꜔-im˧˧ huaŋ꜕꜔-ũã˨˩˨ tsɯ꜕꜔-sia˥˨。

在各种拼音方案之间转换时，请使用 pujbase 项目目录下的 puj.py 脚本（具体选项可通过 --help 获取帮助）：
例如：

```shell
python puj.py --convert puj2dp --input "pheng1-im1"
```

输出：
```
pêng1-im1
```
