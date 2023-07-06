import { DataSource, DeepPartial, FindOptionsWhere, Repository } from 'typeorm';
import { Data } from './data.entity';
import { Injectable } from '@nestjs/common';

@Injectable()
export class DataRepository extends Repository<Data> {
	constructor(
		dataSource: DataSource = new DataSource({
			connectorPackage: 'mysql2',
			type: 'mysql',
			name: 'default',
		}),
	) {
		super(Data, dataSource.createEntityManager());
	}

	async findAll(): Promise<Data[]> {
		return await this.find();
	}

	async findOneBy(args: FindOptionsWhere<Data>): Promise<Data> {
		return await this.findOneBy(args);
	}

	async createData(createDataInput: DeepPartial<Data>): Promise<Data> {
		const data = this.create(createDataInput);
		return await this.save(data);
	}

	async removeData(arg: FindOptionsWhere<Data>): Promise<Data> {
		const data = await this.findOneBy(arg);
		await this.remove(data);
		return new Data('', '', '', false);
	}
}
