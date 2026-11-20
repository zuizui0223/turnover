# 全球452実験のCE/SEを、新しい研究に予測できるか：FDの一般化検証結果

**2026-11-20 実測値で解析、独立集計QA別途。** 原著 Chen, Xiao & Chen (2025), *Nature*, DOI 10.1038/s41586-024-08407-8、公開 [Figshare 27316062](https://doi.org/10.6084/m9.figshare.27316062) の実際のCC BY 4.0原著版v1、29ファイル全件認証なし取得・MD5照合。元の **4,598混植行、452著者StudyID**を確認し、原著の葉窒素FD 2,273行/213 StudyID、SLA FD 2,784行/247 StudyIDと一致。**CE+SE=DY**の原著算術恒等式は実際の対象において不一致0。前者452の中でsource metadata, publication and cohort structure is distinct from source selection of authors; no re-distribution of raw TRY or experimental records.

## 比較の目的（既報相関の再発見ではない）

原著は既に葉N FDやPDとCEの正関係、単植種間生産不均等性とSEの関係を報告している。今回の**別の推定対象**は、元の研究ID `StudyID` 全体を留保したとき、葉N／SLAの「植栽組成から求めたRaoQ」が CE と SE のどちらに**追加の予測精度**を与えるかである。著者の外れ値除去後データを固定し、**同じStudyIDの観測が学習とテストに交差しない**。元原著結果は公開済みのため予測比較も *retrospective study-heldout reanalysis*。単なる生物多様性の独立実験追試ではない。

### 元のモデルはHOLDしたまま

元の事前指定 v0.1 は `Eco1` と `PlantType` のカテゴリダミーが完全に重複し、葉N **116/116**・SLA **127/127** training foldsで行列ランクが1つ不足。[原著説明変数だけを使ったrank診断 Actions #44760950900](https://github.com/zuizui0223/turnover/actions/runs/44760950900)で確定し、**元のv0.1は解析せずHOLD**。これは効果を見て採用条件を緩めたのではない。

生物学的アウトカムを開く前に、重複する `PlantType` のモデル係数だけを除く**別仕様v0.2**を固定した。元データの完全ケース判定には引き続きPlantType元列を要求して**同じ対象行を維持**。他の採用条件、反応CE/SE、FD、研究全体の除外fold、学習研究等重みWLS、bootstrap 2000の変更なし。

固定 M0: `log2(SR)+log1p(StandAge_year)+PD+CWMLN/CWMSLA+MAT+AI+N-fixer mix+Eco1`。固定 M1: M0 + 元の植栽組成由来**RaoQLN**（SLA感度では**RaoQSLA**）。混植後の `RaoQLN_harvest` 等は*結果の影響を受けうるため除外*。元研究の `FD_biomass` もSEと数学的に結びつく可能性から主解析の説明変数に入れない。全ての数値尺度は学習研究のみで標準化。両応答CE/SEは符号を保ち対数変換しない。推定スコア：各研究を等重みとする留保 SSE 増分 `1−SSE(M1)/SSE(M0)`。不確実性は研究IDを2,000回再標本化した**固定済み予測誤差のCI**（各ブートストラップでモデル再推定はしない）。

## 原データの実際の採用集団

| Cohort | 著者の元データ | 完全ケース | 元の研究ID | 5行以上ある研究ID |
|---|---:|---:|---:|---:|
| 葉N FD | 2,273行・213 StudyID | **1,709行** | **116** | **47** |
| SLA FD | 2,784行・247 StudyID | **2,031行** | **127** | **55** |

元の事前固定共変量不足によって葉N 564行/SLA 753行を除外。**この欠測はランダムではない可能性がある。** 研究数は「原著StudyID」の数であり、著者別出版物DOIを照合した独立論文数とは限らない。少数研究による偏りはsource-cluster bootstrapでも完全には消えない。

## 実際の研究留保効果

| 元の形質FD | 補完性CEのFD追加予測SSE改善 | 選択SEのFD追加予測SSE改善 | CE改善−SE改善 |
|---|---:|---:|---:|
| **葉N RaoQ** | **+0.767%**（95%CI −2.866〜+3.662） | **−1.185%**（95%CI −1.957〜−0.497） | **+1.953ポイント**（95%CI −1.593〜+5.083） |
| **SLA RaoQ** | **−0.126%**（95%CI −0.770〜+0.469） | **+0.044%**（95%CI −1.878〜+2.119） | **−0.170ポイント**（95%CI −2.201〜+1.782） |

**重要なのは、葉N FDを追加してCEが良くなる確実な証拠はなく、CEとSEへの追加予測改善率の差も0を跨いだこと。** 葉N FDのSE予測はこの固定モデル・固定ブートストラップ定義では悪化（全区間が負）したが、**FDが生物学的にSEを抑制したことではない**。SLA感度はCE/SEとも概ね0付近。葉NのCE改善で正のStudyIDは**63/116**、SE改善で正は**46/116**；SLAではCE **56/127**、SE **58/127**。

Supplementary signed `CE−SE` を直接予測したFD増分は、葉N **+0.036%**（95%CI −3.258〜+2.186）、SLA **+0.135%**（95%CI −1.262〜+1.397）で、こちらも不明確。CE−SEが必ずFDで予測できると誤って主張しない。

## 何を発見したか／何を発見していないか

- **支持する新しい診断**：既報の「葉N FDとCEのプールした正関連」は、richness/PD/CWM/Nfix/age/climate/ecosystemを同じ基準に入れた**まったく未知の元研究への追加予測情報**とは同義ではない。分野をまたぐ一般化は自明ではなく、source-qualified source-cohortでは**はっきりした正の増分を検証できなかった**。著者の研究内関連結果を否定する主張でもない。
- **支持しない**：FDがCEよりSEを予測する、FDが普遍的にNDEを引き上げる、FDがCEとSEの因果的割り当てを操作する、BIEN K/ρ→FD→CE/SE→絶対バイオマス媒介鎖、原著の452独立実験への我々独立データによる再現、永続的な地域に不変の規則。
- **重大制限**：元著者が4,680から82混植観測を結果側の標準化残差で除外した原データを使っている。葉N/SLAコホートの共変量欠測でStudyIDの約半分が失われる。StudyIDが完全に重複なし独立論文に対応するか未監査。正/負効果のCIは固定LOSO誤差ベクトルのStudyIDクラスター再標本で、ブートストラップ内の推定器変動やデータ収集労力は加味していない。著者が実際に栽培/無作為化したのは種数や種組み合わせで、FD連続量を独立に割り付けてはいない。

## 検証と再現性

- [Official Figshare 29/29 file and checksum source access #44757843070](https://github.com/zuizui0223/turnover/actions/runs/44757843070).
- [Five original source cohorts exact rows/columns #44758861235](https://github.com/zuizui0223/turnover/actions/runs/44758861235).
- [Unfittable original v0.1, 116/127 model rank HOLD #44760473697](https://github.com/zuizui0223/turnover/actions/runs/44760473697).
- [Predictor-only rank diagnostic #44760950900](https://github.com/zuizui0223/turnover/actions/runs/44760950900).
- [Fixed outcome-blind revised v0.2 source gate and real CE/SE study-heldout CV #44761456911](https://github.com/zuizui0223/turnover/actions/runs/44761456911), original signed source-effect values never committed; artifact #14640719071 SHA256 `dbf39722cc77adc07694c6448af084a7e995d522a7a84dc8849b4171d31a4344`.
- Persistent results `results/chen452_leafn_sla_fd_ce_se_studyholdout_v0_2.json`; full reproducible original-source Python and separate source-only fixed protocol in this Draft. Nothing merged to `main`.
