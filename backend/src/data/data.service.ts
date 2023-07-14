import { FindOptionsWhere, Repository } from 'typeorm';
import { Data } from './data.entity';
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';

@Injectable()
export class DataService {
	constructor(
		@InjectRepository(Data)
		private dataSource: Repository<Data>,
	) {}

	// Section: Data
	async findDataAll(): Promise<Data[]> {
		return await this.dataSource.manager.find(Data);
	}

	async findDataOneBy(args: FindOptionsWhere<Data>): Promise<Data | Error> {
		return (
			(await this.dataSource.manager.findOneBy(Data, args)) ??
			Error('Data not found')
		);
	}

	async createData(createDataInput: Data): Promise<Data> {
		const data = this.dataSource.manager.create(Data, createDataInput);
		return await this.dataSource.manager.save(Data, data);
	}

	async removeData(arg: FindOptionsWhere<Data>): Promise<void> {
		const data = await this.findDataOneBy(arg);
		await this.dataSource.manager.remove(Data, data);
	}
}
