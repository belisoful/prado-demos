<?php

class Sample6 extends TPage
{
	protected function getData()
	{
		return [
			['id' => 'ITN001', 'name' => 'Motherboard', 'quantity' => 1, 'price' => 100.00],
			['id' => 'ITN002', 'name' => 'CPU', 'quantity' => 1, 'price' => 150.00],
			['id' => 'ITN003', 'name' => 'Harddrive', 'quantity' => 2, 'price' => 80.00],
			['id' => 'ITN004', 'name' => 'Sound card', 'quantity' => 1, 'price' => 40.00],
			['id' => 'ITN005', 'name' => 'Video card', 'quantity' => 1, 'price' => 150.00],
			['id' => 'ITN006', 'name' => 'Keyboard', 'quantity' => 1, 'price' => 20.00],
			['id' => 'ITN007', 'name' => 'Monitor', 'quantity' => 2, 'price' => 300.00],
			['id' => 'ITN008', 'name' => 'CDRW drive', 'quantity' => 1, 'price' => 40.00],
			['id' => 'ITN009', 'name' => 'Cooling fan', 'quantity' => 2, 'price' => 10.00],
			['id' => 'ITN010', 'name' => 'Video camera', 'quantity' => 20, 'price' => 30.00],
			['id' => 'ITN011', 'name' => 'Card reader', 'quantity' => 10, 'price' => 24.00],
			['id' => 'ITN012', 'name' => 'Floppy drive', 'quantity' => 50, 'price' => 12.00],
		];
	}

	protected function populate($data)
	{
		$this->Repeater->DataSource = $data;
		$this->Repeater->dataBind();
	}

	public function onLoad($param)
	{
		parent::onLoad($param);
		if (!$this->IsPostBack) {
			$this->populate($this->getData());
		}
	}

	public function pageChanged($sender, $param)
	{
		$this->Repeater->CurrentPageIndex = $param->NewPageIndex;
		$this->populate($this->getData());
	}

	public function itemCommand($sender, $param)
	{
		if ($param->CommandName === 'select') {
			$key = $this->Repeater->DataKeys[$param->Item->ItemIndex];
			$this->Result->Text = 'You selected ' . $key . '.';
		}
		// The repeater rebuilds its items from view state on a postback, but the
		// databind expressions are not re-evaluated, so the cells would come back
		// empty. Rebinding refills them. CurrentPageIndex is kept in view state,
		// so the same page is shown again.
		$this->populate($this->getData());
	}

	public function bindEmpty($sender, $param)
	{
		$this->Repeater->CurrentPageIndex = 0;
		$this->populate([]);
	}

	public function bindProducts($sender, $param)
	{
		$this->Repeater->CurrentPageIndex = 0;
		$this->populate($this->getData());
	}
}
