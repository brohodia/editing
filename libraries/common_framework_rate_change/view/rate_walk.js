/* eslint-disable */
import * as HX from "hx-model-components";

// Constants
const full_amounts = [
  "actualPremium",
  "technicalPremium",
  "aggregateExposure",
  "mainLimit"
]

const metrics = [
  "technicalRateAdequacy",
  "rateOnExposure",
  "rateOnLimit"
]

const change_amounts = [
  "actualPremiumChgAmt",
  "technicalPremiumChgAmt",
  "aggregateExposureChgAmt",
  "mainLimitChgAmt"
]

const change_pct = [
  "actualPremiumChgPct",
  "technicalPremiumChgPct",
  "aggregateExposureChgPct",
  "mainLimitChgPct",
  "rateAdequacyChgPct",
  "rateOnExposureChgPct",
  "rateOnLimitChgPct",
  "rateLevelChgPct"
]

// Clean up the addition of ratingResult to each string
// Can make use of read only function
const scenarios = [
  "expiring/ratingResult",
  null,
  "renewalStructure/ratingResult",
  "renewalExposure/ratingResult",
  "renewalLossHistory/ratingResult",
  "renewalSubjectiveModifiers/ratingResult",
  "rate/ratingResult",
  null,
  "quote/ratingResult",
  "absolute/ratingResult",
  "percentage/ratingResult"
]

const globals = "quote/interim/uiControls/rateWalk"

function rate_walk(inputPath) {
  return (

    < HX.Section title="Rate Walk" >
      <HX.Pane stretch>
        <HX.Collection
          fields={['results_granularity']}
          with={globals}
        />
        <HX.Collection
          fields={['output_layer_selection']}
          with={globals}
          shownBy='show_layer_selector'
        />
      </HX.Pane>


      <HX.Pane stretch>
        <HX.Pane stretch>
          <HX.Table
            title="Full Amounts"
            data={scenarios}
            fields={full_amounts}
            with={inputPath}
            transpose
            kb-interactive
          />
        </HX.Pane>
        <HX.Pane stretch>
          <HX.Table
            title="Change Amount"
            data={scenarios}
            fields={change_amounts}
            with={inputPath}
            transpose
            kb-interactive
          />
        </HX.Pane>
        <HX.Pane stretch>
          <HX.Table
            title="Metrics"
            data={scenarios}
            fields={metrics}
            with={inputPath}
            transpose
            kb-interactive
          />
        </HX.Pane>
        <HX.Pane stretch>
          <HX.Table
            title="Change %"
            data={scenarios}
            fields={change_pct}
            with={inputPath}
            transpose
            kb-interactive
          />
        </HX.Pane>
      </HX.Pane>
    </HX.Section>

  )
}


export { rate_walk };