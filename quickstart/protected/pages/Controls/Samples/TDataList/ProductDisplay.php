<?php

/**
 * A templated item renderer for the TDataList in Sample3.
 * The renderer's template is ProductDisplay.tpl, which PRADO finds by name.
 */
class ProductDisplay extends TDataListItemRenderer
{
	/**
	 * The data row is available from the Data property once the parent
	 * data list binds this item.
	 */
	public function getSubtotal()
	{
		return $this->Data['quantity'] * $this->Data['price'];
	}

	public function getOriginLabel()
	{
		return $this->Data['imported'] ? 'Imported' : 'Domestic';
	}
}
