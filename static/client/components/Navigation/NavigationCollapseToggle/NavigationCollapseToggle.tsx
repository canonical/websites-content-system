import { Button, Icon, Tooltip } from "@canonical/react-components";
import classNames from "classnames";

const NavigationCollapseToggle = ({
  isCollapsed,
  setIsCollapsed,
  className,
}: {
  isCollapsed: boolean;
  setIsCollapsed: (isCollapsed: boolean) => void;
  className?: string;
}): JSX.Element => {
  return (
    <Tooltip
      message={<>{!isCollapsed ? "collapse" : "expand"}</>}
      position="left"
      tooltipClassName="p-side-navigation--tooltip"
    >
      <Button
        appearance="base"
        aria-label={`${!isCollapsed ? "collapse" : "expand"} main navigation`}
        className={classNames("is-dense has-icon l-navigation-collapse-toggle", className)}
        onClick={(e) => {
          setIsCollapsed(!isCollapsed);
          // Make sure the button does not have focus
          // .l-navigation remains open with :focus-within
          e.stopPropagation();
          e.currentTarget.blur();
        }}
      >
        <Icon name="close" />
      </Button>
    </Tooltip>
  );
};

export default NavigationCollapseToggle;
