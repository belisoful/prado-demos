<?php

/**
 * A templated item renderer for the TTemplateColumn in Sample7.
 * The renderer's template is StockCell.tpl, which PRADO finds by name.
 */
class StockCell extends TDataGridItemRenderer
{
	public function getStockLevel()
	{
		$quantity = $this->Data['quantity'];
		if ($quantity >= 25) {
			return 'plenty';
		}
		return $quantity >= 5 ? 'low' : 'critical';
	}

	public function getStockColor()
	{
		switch ($this->getStockLevel()) {
			case 'plenty':
				return 'green';
			case 'low':
				return 'darkorange';
			default:
				return 'red';
		}
	}
}
