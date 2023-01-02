import * as HX from "hx-model-components";


import UserLib1 from "libraries/helper_functions/view/helper";

const userLib1 = UserLib1();

function HXModel() {
  return (
    <HX.Root>
      <HX.Page>{userlib1}</HX.Page>
    </HX.Root>
  );
}

export default HXModel