# FD、機能群組成、バイオマス：肯定結果の監査と次に検証すべき問い
更新：2026-11-20。**既報・既存再解析の証拠監査であり、新しい統計結果ではない。**

## 主張の階層を分離する

異なる3つの推定対象を混同しない。

1. **実験的な種数／混植割付 → 生産量**：試験区へ種数・種組成を割り付けた処理の総効果は、適切な実験対照・無作為化下で因果解釈が可能。これだけではFDの媒介因果効果は推定しない。
2. **植栽前の形質差 FDis → 混植超過効果**：`log(B_mix/B_expected_monocultures)` に対する予測／関連。適切な単植区のサイト・年ごとの期待値が必要。FDが種数・種組成に従属する場合、通常の回帰係数を「FDだけの介入効果」と呼ばない。
3. **実測群集FD → 絶対バイオマス**：植生現存量と同時点のFDの予測。環境・林齢・CWM・種アイデンティティが強く関与し、同時測定形質は生育の結果にもなりうる。M1追加予測SSE増分の失敗は、混植効果そのものが負であることを意味しない。

### 既存の肯定結果と反証的な境界

| エビデンスと推定対象 | 結果 | 証拠の正しい位置づけ |
|---|---|---|
| Jensen et al. 2026 TreeDivNet：FDis と木本混植 NDE | 原著の単純関連 β=+0.27, p<0.001。6実験のSEM中でFD→木本NDEの標準化係数 +0.46, p=0.0003 | **原著による既報の正関連**、われわれの独立再現結果ではない。SEM経路は介入によるFD因果効果ではない |
| Jensen et al. 2026：混植に伴う光獲得形質・木本NDE | SLAの混植差は種レベル平均約+7% (p=0.004)。6実験のSEMでSLA NDE→木本 NDE +0.29 (p=0.002)、LAI NDE→木本 NDE +0.48 (p<0.0001) | 正の関連経路。原著では**間接媒介効果は確認されず、すべて直接経路**である点に注意 |
| Cedar Creek E120 1998（PR #44）：機能群の数 vs アイデンティティ | 94試験区。元の種数・Woody・FG count・18フィールド行を条件化後、4群係数の異質性 HC3 p=2.58e-5、条件付きベクトルシャッフル p=0.0070 | **われわれの再解析のソース内肯定結果**。単一実験・二次教育表。種アイデンティティとギルドが絡み、窒素固定の因果機構は不明 |
| BIODEPTH 8実験地（PR #45）：grass+legume vs grass+other forb | 種数・サイト・ブロックを合わせた110区画、6/8サイトが正。8サイト等重み平均 log1pバイオマス差 +0.17147、95% CI [-0.54832,+0.91837] | 正の記述的方向だが**プール効果の正値は未確定**。種組成も同時変化 |
| Jena 2003（PR #40）：FG数と5月バイオマス | log2種数調整で β=+0.16789, p=0.0439。しかし正確な種数カテゴリー・ブロック調整の62試験区で β=+0.12867, p=0.1676 | モデル仕様に依存、正の効果とは判定できない。Jena機能群アイデンティティはCedarの独立再現を示さない |
| BIODEPTH 2010（PR #46）：高さFD→絶対地上部現存量の未知サイト予測 | 原 GIFT *Origanum vulgare* 13m 値で−123.09%のSSE増分。Kew 0.90m感度で+3.83%、95% CI [-10.92,+18.29] | FDの独立した正の予測増分は**確認されない**。一種の異常形質値に敏感 |
| TreeDivNet 別推定対象（PR #57）：実際の区画内SLA+LNCMによるFD→未知実験の**絶対木本現存量** | 113区画/6研究・2/6正、研究等重み増分−34.91%、研究ブートストラップ95% CI [-70.78,-1.56] | 追加予測が不安定／不利。ただし原著の単植基準に対する相対的混植利得NDEとは**応答もFD定義も違う**。負のFD因果効果ではない |
| Chen et al. 2025 Nature：452種多様性操作実験のメタ解析 | 平均2.6種の混植は単植に比べ生産力が平均+15.2% | 異なる生態系にまたがる**種多様性・混植総効果**の独立文献証拠。FD固有の操作効果は証明しない |
| 2026 Nature E&E：75生物多様性実験の乾燥環境メタ解析 | 乾燥した草地の極端干ばつでは、補完性による多様性効果が強まる。森林では同様の明確な応答は限定的 | 広域の**環境文脈依存性**。FD→NDEの新規介入推定ではない |

**参照元：** [Jensen 2026 DOI 10.1111/1365-2435.70320](https://doi.org/10.1111/1365-2435.70320);
[Chen et al. 2025 DOI 10.1038/s41586-024-08407-8](https://doi.org/10.1038/s41586-024-08407-8);
[2026 aridity study DOI 10.1038/s41559-026-03130-1](https://doi.org/10.1038/s41559-026-03130-1);
[turnover PR #44](https://github.com/zuizui0223/turnover/pull/44),
[#40](https://github.com/zuizui0223/turnover/pull/40),
[#45](https://github.com/zuizui0223/turnover/pull/45),
[#46](https://github.com/zuizui0223/turnover/pull/46),
[#57](https://github.com/zuizui0223/turnover/pull/57).

## Jensen原著の最重要制限

原著のFDisは主に同一サイトの**単植区測定値 283**と不足時のデータベース値 **17**から作り、植栽種を等重みとしている。著者はFDisを種数に関連する代理勾配としても解釈している。したがって「FDisが正に関連した」ことは「種数・植栽アイデンティティを操作せずFDだけの独立因果効果が認められた」と同義ではない。6実験のSEMでは、FD→NDE_SLA/LAI→NDE_woodyという**媒介効果**を検証的に確立したのではなく、すべての推定経路は直接関係であった。

## 次に問うべき新しいこと（現時点では仮説）

**「FDは木本バイオマスの絶対量ではなく、単植の期待値を上回る混植の利得を、資源環境に条件付きで予測するか」**。

一つの記号で応答の取り違えを防ぐ：

```
log(B_mix) = log(B_expected from site-year matched monocultures)
             + log(NDE_mix)
```

`B_expected` はサイト固有の絶対的な生産能力・種単独生産性の一部を表す。一方 `NDE_mix` は単植基準の超過分を捉える。したがって絶対現存量へのFD追加予測が失敗しても、FD→超過生産の関連は正でありうる。**既存の正負の結果は、この区別を支持する「対照例」であり、同一データで効果を比較する直接検定ではない。**

次の独立原データで、**生態学的応答を閲覧する前に**次を凍結し、採用条件に合格した場合だけ解析する：

- 原著の無作為化設計と独立研究地点を同定。単植の期待値を**同じ研究・同じ年・同じ種**から作れること。種組成・混合割合・初期種数・単植プロット数・空間ブロックを確認。
- FDは混植後の反応形質ではなく**単植由来／植栽前の形質**を優先。種数・形質平均CWM・種アイデンティティを適切に調整した**独立FD情報**が設計上識別可能かを、バイオマス応答を見る前に判定する。種数とFDがほぼ同じなら SOURCE/DESIGN HOLD。
- 主応答 `log(NDE_mix)` と対照 `log(B_mix)` を同じ元の混植区画で比較、追加FDは完全な独立実験を一つずつ留保して評価。図の係数でなく、実験外予測SSEと各研究間の推定範囲を主要指標とする。
- 水分制限、林齢、森林／草地の差、土壌養分など**事前に指定した環境文脈の交互作用**だけを検証。乾燥効果は既知のため、単なる既報追認を新規性として扱わない。
- 無作為に割り付けた植栽種数・植栽組成の**総効果**と、連続FDに帰属させる**媒介因果効果**を区別する。植栽後に測ったSLA/LAIをFD→生産の媒介としてSEMに投入しても、未測定の交絡を制御・時間順序を確認しない限り因果的媒介を宣言しない。

**新規性の境界：** 多様性が生産量を増やすこと、FDisとNDEが正に関連すること、乾燥草地で補完性が増すこと自体は既報。潜在的に新しいのは、異なる実験・生態系で**絶対量と超過生産へのFD予測性能が系統的に異なるか、その差が資源文脈で再現するか**を、独立研究の留保で検定すること。

## 系統的記憶K/ρとの関係

2026-11-20時点で**K/ρ→群集FD→バイオマスの完全な媒介因果鎖は未成立**。科×形質記憶の移植可能性（RC4）と、FDの混植超過生産への関係は別論文の推定対象。原著Kの分布や元データを付け足して因果鎖を「完成」と呼ばない。将来独立標本・十分な科種数・標本対応が満たされれば上位仮説として検証する。


## 2026-11-20 original-source extension: 21 experiments, paired mechanistic outcomes, independent grassland

A separate source-only [PR #68](https://github.com/zuizui0223/turnover/pull/68) froze the next cross-experiment question before accessing original response rows. The **independently identified published 2025 Jensen TreeDivNet data release** [Dryad DOI 10.5061/dryad.dz08kps9x](https://doi.org/10.5061/dryad.dz08kps9x) advertises **1,609 plots from 21 experiments, five continents** with `DS1` absolute annual basal-area productivity, `DS2` FD + annual productivity, `DS3` matching mixture NDE/selection/complementarity + WD/LNC FDis and CWMs. In the original [GCB article DOI 10.1111/gcb.70493](https://doi.org/10.1111/gcb.70493), the authors already established positive species-richness productivity, a predominance of selection effects (**77% of NDE**), and higher selection effects with higher wood-density trait diversity. **These are published original-author results, not new findings from our reanalysis.** The 2025 and 2026 Jensen sources overlap in the original TreeDivNet network; never count them as independent study cohorts without explicit original experiment crosswalk.

The independent Swiss **PaNDiv** grassland experiment has original 2022 [Dryad DOI 10.5061/dryad.zs7h44jbp](https://doi.org/10.5061/dryad.zs7h44jbp) (**336 source plot IDs**, published species×plot×harvest estimated biomass, pre-sown SLA CWM and mean pairwise SLA dispersion) and a distinct 2025 [Dryad DOI 10.5061/dryad.1c59zw47k](https://doi.org/10.5061/dryad.1c59zw47k) (**216 plots**, 2017–2023 aboveground biomass release). Published [Cappelli et al. 2022](https://doi.org/10.1002/ecm.1521) reports **positive average complementarity, negative selection in plant biomass**. The opposing components in Jensen and PaNDiv motivate *environmental/assembly-dependent allocation of diversity benefits*, but 21 network experiments versus one Swiss grassland cannot alone identify a universal forest–grassland difference.

**Executed original source gate** [Actions #44748888990](https://github.com/zuizui0223/turnover/actions/runs/44748888990): all three official original Dryad DOI/API metadata read successfully; first original downloadable file returned **HTTP 401 in every release**. No original response rows or ecological models were opened, and source design remains **ACCESS_HOLD**. This is not evidence of FD biological failure.

A distinct **small-scale method pilot** [PR #69](https://github.com/zuizui0223/turnover/pull/69) uses original Cadotte 2017 mixed-plant data [Zenodo #5022435](https://zenodo.org/records/5022435) with 40 published mixture NDE/selection/complementarity responses, pre-sown traits and original plot biomass. Its original article [Cadotte 2017 Ecology Letters DOI 10.1111/ele.12796](https://doi.org/10.1111/ele.12796) **already reported selection strongest at low trait dissimilarity and complementarity strongest at high dissimilarity**. The pilot therefore tests *retrospective same-mixture predictive estimand feasibility*, not independent original biological replication, and has no multi-study generalization. Do not promote any pilot result to prospective or causal without new independent experiments.

### Revised inference prioritization

The robust causal claim currently supported by manipulative experiments is the **total effect of planted species mixture/richness/composition**, conditional on allocation and design. The hypothesized chain **pre-sowing FD → NDE through selection/complementarity → biomass** remains a mechanistic pathway, not a proven FD-only intervention or a validated BIEN family-specific phylogenetic-memory mediation. When original data become available, use *identical plot sets and whole-experiment holdouts* for absolute productivity and NDE, report both signed NDE and its components, and never log-transform signed component values. Do not count forest and grassland publications sharing original experiments as independent biological replications.


## 2026-11-20 実測 Cadotte 2017 探索的予測照合（公開原データ使用、因果解釈なし）

[PR #69](https://github.com/zuizui0223/turnover/pull/69) では公開原著 Zenodo 5022435 の4 CSV のMD5を照合し、元の**40混植区**、**14種の形質**、**34種組成の留保単位**を正確に結合した。全40区で原著 `COMP+SELECT=DeltaY` が成立し、別表の絶対バイオマスと整合（許容誤差外0）、植栽種数と元の種リストも一致した。種を植える前の2形質（log SLA・log height）から作るFDを、種数＋形質平均CWMのベースモデルに追加し、組成を丸ごと除外する予測で比較した。モデル・応答・変換は計算前に固定したが、原著の正の関係を見た後の単一実験のため**retrospective exploratory**である。

| 同一区画の応答 | FD追加の留保組成SSE改善 | 95%組成ブートストラップCI |
|---|---:|---:|
| 絶対地上部バイオマス | **+8.82%** | −13.51%〜+25.78% |
| NDE（元の符号付きDeltaY） | **−3.62%** | −15.52%〜+4.09% |
| 補完性（COMP） | −6.25% | −15.15%〜+0.08% |
| 選択（SELECT） | −1.24% | −10.06%〜+3.11% |

**事前指定したNDE改善−絶対量改善 = −12.44ポイント、95%CI [−26.56,+0.84]ポイント。** 予想した「FDは絶対量よりNDEを良く予測する」は**この試行では支持されなかった**。逆方向の普遍性も、CIが0を跨ぐため証明されない。固定された学習済み予測残差を34原組成単位でブートストラップ（1000回）した近似CIであり、モデル再推定ブートストラップではない。元の論文はすでにFDと選択・補完性の関係を報告しているので独立確認を名乗らない。

**重要な含意:** 「FDと補完性／NDEの原著正相関」と「種数・CWMを超えたFDの独立した留保組成予測利得」は**違う推定対象**である。原著の正相関が成立してもこの追加予測が確立するとは限らない。NDEや選択・補完性は符号付きなので対数変換しない。原著の生物種組成がFDと同時に変わるためFDだけの因果介入効果ではなく、K/ρ→FD→バイオマスの媒介連鎖でもない。

[実測CI #44750171096](https://github.com/zuizui0223/turnover/actions/runs/44750171096)、[独立集計QA #44751586875](https://github.com/zuizui0223/turnover/actions/runs/44751586875)。この1実験40区を21森林実験／PaNDivと合算したメタ解析とは呼べない。TreeDivNet 2025・PaNDiv 2022/2025 の原データは引き続きオリジナルDryadダウンロードHTTP401＝SOURCE_ACCESS_HOLDであり、それらに新しい係数は存在しない。


## 2026-11-21 原データによるJena TBE混植収量分解：FDから機構に近づけるが因果は未成立

**同一研究を繰り返し「独立研究」と数えない。** Wagg et al. 2017のオリジナルJena Trait-Based Experiment は、2002年のJena Main Experimentとは**別の設計**ながら**一つの野外実験**である。原PANGAEA [10.1594/PANGAEA.876725](https://doi.org/10.1594/PANGAEA.876725)、CC BY 3.0。元の **138植栽区画（2012年のMay/Aug合計276観測）、24真正単植区（種プールごと8種）、114混植区**から、**事前に固定した6種プール×植栽種数層の高FD≥3／低FD≤2、84元混植区**を全く同じ母集団・重みで比較した。[原データ/割付 source PR #72](https://github.com/zuizui0223/turnover/pull/72)、[年間絶対量 PR #73](https://github.com/zuizui0223/turnover/pull/73)、[単植期待・Loreau–Hector CE/SE/NDEによる原データ分解 PR #74](https://github.com/zuizui0223/turnover/pull/74)。

**同じ元データ・区画・設計から算出した高FD−低FD調整差**（単位 g乾燥重量/m²、全て2000回元区画ブートストラップ95%区間）：

| 応答／成分 | 点推定 | 95%CI |
|---|---:|---:|
| 元のプール固有単植からの期待量 E | **−33.62** | **[−94.17, +32.13]** |
| 混植超過利得 NDE | **+68.96** | **[−24.63, +163.53]** |
| 補完性成分 CE | **+27.81** | **[−47.63, +104.01]** |
| 選択成分 SE | **+41.15** | **[−26.80, +104.39]** |
| 観測された年間混植バイオマス B | **+35.34** | **[−76.28, +146.73]** |

**独立に原データから証明できた会計式**：
`+35.34 = −33.62 + 68.96`（`B=E+NDE`）かつ `+68.96=+27.81+41.15`（`NDE=CE+SE`）。各84原混植区のCE+SE−NDEの最大計算残差は**2.27e−13 g/m²**。これによって**「混植の超過利得が大きい点推定」と「群集絶対量の増分が小さい点推定」が元の単植期待生産能力の違いによって同時に成り立つ**ことを、同一元データで示した。ただし**5項目すべての95%CIは0を含み、符号も因果効果も確定しない**。数式恒等式自体は新しい進化・生態学的原理ではない。

**source/causal gate未解決**：原PANGAEA `Block` 列は1種類、論文には3空間無作為化ブロックと記載。Plot ID A/B/Cが各46区画という均衡は確認したが、**物理的な無作為化Blockとの正規対応はJEXIS #739タイムアウトで未確定**。3系列はあくまで非認証の説明用空間proxyであり、**元の厳密な因果実験source gateはHOLD**。さらに設計されたFD区分を操作すると植栽種アイデンティティが一緒に変わるため、連続FDの独立した因果操作ではない。各種単植が実質1区画なので、84混植区のplot bootstrapは単植期待値の標本誤差を伝播しない。元Wagg論文はすでに空間・時期資源利用による補完性の関係を研究しており、ここで新しい独立実験として再発見したとは扱わない。

Source empirical runs: [#44847711261](https://github.com/zuizui0223/turnover/actions/runs/44847711261) (DOI+source eligibility), [#44847964061](https://github.com/zuizui0223/turnover/actions/runs/44847964061) (plot prefix/JEXIS), [#44848307503](https://github.com/zuizui0223/turnover/actions/runs/44848307503) (84 annual biomass), [#44848773717](https://github.com/zuizui0223/turnover/actions/runs/44848773717) (24 mono, CE/SE/NDE), [#44849069631](https://github.com/zuizui0223/turnover/actions/runs/44849069631) (observed=expected+NDE same source) and [#44849252682](https://github.com/zuizui0223/turnover/actions/runs/44849252682) (independent aggregate-number/CI identity). All numeric outputs are nonraw; no original plot/species data redistributed.

**科学的優先順位**：元の「FDは生産を増やすか？」という問いだけではなく、**同じ混植が単植期待量をどれだけ上回るか、その超過分がCEかSEか**を区別することが重要。しかし本例でその成分が高FDのために増えた確定的な根拠はない。次に必要なのは、真の原設計Blockと植栽種の無作為割付が検証できる独立実験群で同じ固定比較を行い、単植推定値の不確実性まで同時に伝播すること。**K/ρ→FD→CE/SE→biomassの因果媒介鎖は未実証のまま**。
